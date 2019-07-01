import os
from datetime import date
from typing import Optional, Tuple, Dict
import logging
import functools
import boto3

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
PKEY_BALLOTS = 'ballots'
PKEY = 'id'
RANGE_KEY = 'sortkey'
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
#   "date": date.today().isoformat(),
#   "votes": {
#       "user": {"id": None, "name": None}
#   }
#
# }

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
    return update_ballot_key(ballot, 'votes', ballot['votes'])

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
    update_ballot_key(ballot, 'places', places)
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

# perhaps we should be updating whole item?
def update_ballot_key(item, key, value):
    log.debug("Updating ballot %s with {%s: %s}", item, key, value)
    return table.update_item(Key={PKEY: item[PKEY], RANGE_KEY: item[RANGE_KEY]},
                             UpdateExpression=f'SET #key = :val',
                             ExpressionAttributeNames={'#key': key},
                             ExpressionAttributeValues={':val': value},
                             ReturnValues="ALL_NEW")

def get_free_id(ids):
    ids = sorted(ids)
    range_end = int(ids[-1]) + 2 if ids else 1
    for n in range(range_end):
        # this could be done with o(n) or even less...
        if n not in ids:
            return n
    raise StopIteration

def table_apply(untabled_function, table):
    return functools.partial(untabled_function, table)

def _dict_to_expression(expr_dict: Dict[str, str]) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    # fold this to big tuple?
    expressions = (f"#{key_name} = :{val_name}" for key_name, val_name in expr_dict.items())
    expression = " AND ".join(expressions)
    attributes = {f":{v}": v for _, v in expr_dict.items()}
    keys = {f"#{k}": k for k, _ in expr_dict.items()}
    return expression, keys, attributes

# api returns dicts, without wrappingfr
def last_items(table, pkey: Tuple[str, str], sortkey: Optional[Tuple[str, str]],
               reverse: bool = False, limit: int = 1) -> list:
    pkeys = filter(lambda x: x, (pkey, sortkey))
    expr_dict = {k: v for k, v in pkeys} # noqa T484
    key_expression, keys, attributes = _dict_to_expression(expr_dict)
    # key_expressions = (f"{key_name} = :{key_name}" for key_name, _ in keys if key_name)
    # key_expression = " AND ".join(key_expressions)
    # attributes = {f":{v}": v for k, v in keys}
    elements = table.query(KeyConditionExpression=key_expression,
                           Limit=limit, ScanIndexForward=reverse,
                           ExpressionAttributeNames=keys,
                           ExpressionAttributeValues=attributes)
    return elements.get('Records', [])

def update_item(table, pkey: Tuple[str, str], sortkey: Tuple[str, str], update_dict: dict) -> dict:
    log.debug("Updating ballot %s with {%s: %s}",)
    pkeys = filter(lambda x: x, (pkey, sortkey))
    expression, keys, attributes = _dict_to_expression(update_dict)
    print(_dict_to_expression(update_dict))
    print(list(pkeys))
    update_expression = f"SET {expression}"
    update_cmd = table.update_item(Key={key: val for key, val in pkeys},
                                   UpdateExpression=update_expression,
                                   ExpressionAttributeNames=keys,
                                   ExpressionAttributeValues=attributes,
                                   ReturnValues="ALL_NEW")
    return update_cmd.get('Attributes', {})


def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    ballot = table.query(KeyConditionExpression=f'{PKEY} = :key',
                         Limit=1, ScanIndexForward=False,
                         ExpressionAttributeValues={':key': PKEY_BALLOTS})
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
