import os
from datetime import date
import boto3

TABLE_NAME = os.environ.get('DYNAMODB_TABLENAME')

# spoiler alert, dynamo db is a bag of trash
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME or 'Luncherbot')
PKEY_BALLOTS = 'ballots'
PKEY = 'id'
RANGE_KEY = 'sortkey'

#
# structure of voting:
# __ ={ PKEY
#   "venues": {
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

def get_venues():
    ballot = get_ballot()
    venues = ballot.get('venues', {})
    return venues

def _get_venue(ballot, venue):
    venue = venue.strip().lower()
    for v_dict in ballot['venues']:
        vid = v_dict['id']
        if venue in (str(vid), v_dict['name'].strip().lower(), f'#{vid}'):
            return v_dict
    return

def add_vote(venue, user):
    ballot = get_ballot()
    venue = _get_venue(ballot, venue)
    ballot['votes'][user] = {"id": venue['id'], 'name': venue['name']}
    update_ballot_key(ballot, 'votes', ballot['votes'])

def add_venue(venue, user):
    ballot = get_ballot()
    venue_lower = venue.strip().lower()
    venues = ballot['venues']
    for v in venues:
        v_name = v.get('name').strip().lower()
        if v_name == venue_lower:
            return False
    n_id = get_free_id([int(i['id']) for i in venues])
    venues.append({'id': n_id, 'name': venue, 'user': user})
    update_ballot_key(ballot, 'venues', venues)
    return True

# if the value gets removed on the same day, it will not persist
def remove_venue(venue):
    ballot = get_ballot()
    venue_lower = venue.strip().lower()
    venues = ballot['venues']
    votes = ballot['votes']
    # not the most elegant
    for v in venues:
        v_name = v.get('name').strip().lower()
        if v_name == venue_lower:
            venues.remove(v)
            for user, vote in votes.keys:
                if f"#{venue_lower}" == vote['name'] or venue_lower == vote['name']:
                    ballot['votes'].pop(user)
            update_ballot_key(ballot, 'venues', venues)
            return True
    return False

# perhaps we should be updating whole item?
def update_ballot_key(item, key, value):
    table.update_item(Key={PKEY: item[PKEY], RANGE_KEY: item[RANGE_KEY]},
                      UpdateExpression=f'SET {key} = :val',
                      ExpressionAttributeValues={':val': value})

def get_free_id(ids):
    ids = sorted(ids)
    range_end = int(ids[-1]) + 2 if ids else 1
    for n in range(range_end):
        # this could be done with o(n) or even less :)
        if n not in ids:
            return n
    raise StopIteration

# i am an idiot
# there is a chance i am an idiot, but boto3 cant translate types
# it really seems like garbage, that a high-level library lacks much
# def dict_to_item(raw):
#     if isinstance(raw, dict):
#         return {'M': {k: dict_to_item(v) for k, v in raw.items()}}
#     elif isinstance(raw, list):
#         return {'L': [dict_to_item(v) for v in raw]}
#     elif isinstance(raw, str):
#         return {'S': raw}
#     elif isinstance(raw, int):
#         return {'N': str(raw)}

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    q = {'KeyConditionExpression': f'{PKEY} = :key AND {RANGE_KEY} = :ballot_date',
         'Limit': 1, 'ScanIndexForward': True,
         'ExpressionAttributeValues': {':key': PKEY_BALLOTS, ':ballot_date': ballot_date.isoformat()}}
    ballot_query = table.query(**q)
    if not ballot_query.get('Count', 0):
        generate_ballot()
        ballot_query = table.query(**q)
        assert ballot_query.get('Count', 0)
    return ballot_query.get('Items')[0]

def generate_ballot():
    ballot = table.query(KeyConditionExpression=f'{PKEY} = :key',
                         Limit=1, ScanIndexForward=True,
                         ExpressionAttributeValues={':key': PKEY})

    if ballot.get('Count'):
        ballot_content = ballot.get('Items')[0]
    else:
        ballot_content = {}
        ballot_content[PKEY] = PKEY_BALLOTS
        ballot_content['venues'] = []

    ballot_content['votes'] = {}
    ballot_content[RANGE_KEY] = date.today().isoformat()
    table.put_item(Item=ballot_content)
