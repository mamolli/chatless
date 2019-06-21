import os
from datetime import date
import logging
import boto3

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

# spoiler alert, dynamo db is a bag of trash
TABLE_NAME = os.environ.get('DYNAMODB_TABLENAME')
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
        vname = v_dict['name'].strip().lower()
        if venue in (str(vid), vname, f'${vid} {vname}', f'${vid}'):
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
        vname = v.get('name').strip().lower()
        vid = v.get('id')
        if venue_lower in (str(vid), vname, f'${vid} {vname}', f'${vid}'):
            venues.remove(v)
            for user, vote in votes.items():
                if f"${venue_lower}" == vote['id'] or venue_lower == vote['name']:
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

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    ballot = table.query(KeyConditionExpression=f'{PKEY} = :key',
                         Limit=1, ScanIndexForward=True,
                         ExpressionAttributeValues={':key': PKEY_BALLOTS})
    log.debug("Generating ballot from: %s", ballot)
    if ballot.get('Count'):
        ballot_content = ballot.get('Items')[0]
    else:
        ballot_content = {}
        ballot_content[PKEY] = PKEY_BALLOTS
        ballot_content['venues'] = []

    ballot_content['votes'] = {}
    ballot_content[RANGE_KEY] = date.today().isoformat()
    log.debug("Generating new ballot: %s", ballot)
    table.put_item(Item=ballot_content)
    return ballot_content
