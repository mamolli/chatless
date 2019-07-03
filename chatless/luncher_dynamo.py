import os
import dynamo
import logging
from functools import partial
import boto3
from datetime import date

log = logging.getLogger()
log.setLevel(logging.DEBUG)


TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
# PKEY = 'id'
# RANGE_KEY = 'sortkey'

PKEY = 'id'
BALLOTS = 'ballots'
SORTKEY = 'sortkey'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

#
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

dt = dynamo.DynamoTableControl(table)
dynamo_ballots = dynamo.DynamoSubsetTableControl(table, (PKEY, BALLOTS))

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    ballot_date_iso = ballot_date.isoformat() 
    ballot = dynamo_ballots.last_items(table)
    ballot_content = next(iter(ballot), {PKEY: BALLOTS, 'places': []})

    if ballot_date_iso != ballot_content.get(SORTKEY):
        ballot_content['votes'] = {}
        ballot_content[SORTKEY] = ballot_date_iso 
        log.debug("Generating new ballot: %s from ballot: %s", ballot_content, ballot)
        table.put_item(Item=ballot_content)
    return ballot_content

def get_places():
    ballot = get_ballot()
    places = ballot.get('places', {})
    return places

def _get_place(ballot, place):
    place = place.strip().lower()
    for v_dict in ballot['places']:
        vid = v_dict['id']
        vname = v_dict['name'].strip().lower()
        if place in (str(vid), vname, f'${vid} {vname}', f'${vid}'):
            return v_dict
    return

def add_vote(place, user):
    ballot = get_ballot()
    place = _get_place(ballot, place)
    ballot['votes'][user] = {"id": place['id'], 'name': place['name']}
    log.debug("Adding vote for %s by %s", place, user)
    return dynamo_ballots.update_ballot_key(ballot, {'votes': ballot['votes']})

def add_place(place, user):
    ballot = get_ballot()
    place_lower = place.strip().lower()
    places = ballot['places']
    for v in places:
        v_name = v.get('name').strip().lower()
        if v_name == place_lower:
            return False
    n_id = get_free_id([int(i['id']) for i in places])
    places.append({'id': n_id, 'name': place, 'user': user})
    dynamo_ballots.update_ballot_key(ballot, 'places', places)
    return True

# if the value gets removed on the same day, it will not persist
def remove_place(place):
    ballot = get_ballot()
    place_lower = place.strip().lower()
    places = ballot['places']
    votes = ballot['votes']
    # not the most elegant
    for v in places:
        vname = v.get('name').strip().lower()
        vid = v.get('id')
        if place_lower in (str(vid), vname, f'${vid} {vname}', f'${vid}'):
            places.remove(v)
            for user, vote in votes.items():
                if f"${place_lower}" == vote['id'] or place_lower == vote['name']:
                    ballot['votes'].pop(user)
            update_ballot_key(ballot, 'places', places)
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

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    dt.last_items((PKEY, PKEY_BALLOTS))
    # ballot = table.query(KeyConditionExpression=f'{PKEY} = :key',
    #                      Limit=1, ScanIndexForward=False,
    #                      ExpressionAttributeValues={':key': PKEY_BALLOTS})
    log.debug("Generating ballot from: %s", ballot)
    query_empty = False if ballot.get('Count') else True
    if not query_empty:
        ballot_content = ballot.get('Items')[0]
    else:
        ballot_content = {}
        ballot_content[PKEY] = PKEY_BALLOTS
        ballot_content['places'] = []

    if ballot_date.isoformat() != ballot_content.get(RANGE_KEY):
        ballot_content['votes'] = {}
        ballot_content[RANGE_KEY] = date.today().isoformat()
        log.debug("Generating new ballot: %s from ballot: %s", ballot_content, ballot)
        table.put_item(Item=ballot_content)
    return ballot_content
