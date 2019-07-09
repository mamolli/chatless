import os
import logging
from functools import partial
import boto3
from datetime import date
from chatless import dynamo

log = logging.getLogger()
log.setLevel(logging.DEBUG)

TABLE_NAME = os.environ.get('DYNAMODB_TABLE')

PKEY = 'id'
BALLOTS = 'ballots'
SORTKEY = 'sortkey'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


# structure of voting:
# __ ={ PKEY
#   "places": {
#       "id": None,
#       "name": None,
#       "added_by": None
#   },
#   RANGE_KEY   : date.today().isoformat(),
#   "votes": {
#       "user": {"id": None, "name": None}
#   }
#
# }

# TODO: append hashmaps for atomic op

dballots = dynamo.DynamoSubsetTableControl(table, (PKEY, BALLOTS))


def get_places():
    ballot = get_ballot()
    places = ballot.get('places', {})
    return places

def _get_place(ballot, place):
    place = stem(place)
    for place_dict in ballot['places']:
        if place in list_comibination(place_dict['id'], place_dict['name']):
            return place_dict
    return

def add_vote(place, user):
    ballot = get_ballot()
    place = _get_place(ballot, place)
    ballot['votes'][user] = {"id": place['id'], 'name': place['name']}
    log.debug("Adding vote for %s by %s", place, user)
    return dballots.put_item(ballot)

def add_place(place, user):
    ballot = get_ballot()
    place_lower = stem(place)
    places = ballot['places']
    for p in places:
        if place_lower == stem(p['name']):
            return False
    free_id = get_free_id([int(i['id']) for i in places])
    places.append({'id': free_id, 'name': place, 'user': user})
    dballots.put_item(ballot)
    return True

def stem(s):
    diactrit_map = {'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ń': 'n', 'ć': 'c'}
    s = ''.join((diactrit_map.get(char, char) for char in s))
    return s.strip().lower()

def list_comibination(item_id, item_name):
    item_name = stem(item_name)
    return (str(item_id), item_name, f'${item_id} {item_name}', f'${item_id}')

# if the value gets removed on the same day, it will not persist
def remove_place(place):
    ballot = get_ballot()
    place_lower = stem(place)
    for p in ballot['places']:
        if place_lower in list_comibination(p['id'], p['name']):
            ballot['places'].remove(p)
            dballots.put_item(ballot)
            return True
    return False

def get_free_id(ids):
    ids = sorted(ids)
    range_end = int(ids[-1]) + 2 if ids else 1
    for n in range(range_end):
        # this could be done with o(n) or even less...
        if n not in ids:
            return n
    raise StopIteration

# def update_ballot(ballot, update_dict):
#     pkey, sortkey = ballot.get(PKEY), ballot.get(SORTKEY)
#     assert pkey and sortkey and update_dict
#     return dballots.update_item((SORTKEY, sortkey), update_dict)

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    ballot_date_iso = ballot_date.isoformat()
    ballot = dballots.last_items()
    ballot_content = next(iter(ballot), {PKEY: BALLOTS, 'places': []})

    if ballot_date_iso != ballot_content.get(SORTKEY):
        ballot_content['votes'] = {}
        ballot_content[SORTKEY] = ballot_date_iso
        log.debug("Generating new ballot: %s from ballot: %s", ballot_content, ballot)
        dballots.put_item(ballot_content)
    return ballot_content
