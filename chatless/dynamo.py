TABLE_NAME = os.environ.get('DYNAMODB_TABLENAME')

# spoiler alert, dynamo db is a bag of trash
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME or 'Luncherbot')
PKEY = "ballots"

#t.query(KeyConditionExpression=Key('id').eq('fdshfjbhdjs'), Limit=1, ScanIndexForward=True)
# t.query(KeyConditionExpression='id = :key', Limit=1, ScanIndexForward=True, ExpressionAttributeValues={':key': 'fdshfjbhdjs'})

# structure of voting:
# __ = {
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
def get_venues(venue):
    ballot = get_ballot()
    venues = ballot.get('venues', {})
    return venues

def add_venue(venue, user):
    ballot = get_ballot()
    venue_lower = venue.strip().lower()
    for v_name in ballot.get['venues'].values():
        v_name = v_name.strip().lower()
        if venue.strip().lower() == venue_lower:
            return False
    return True

def update_key(key, value):


def get_free_id(ids):
    ids = sorted(ids)
    for n in range(ids[-1] + 2):
        # this could be done with o(n) or even less :)
        potential = f'#{n}'
        if potential not in ids:
            return potential

# there is a chance i am idiot, but boto3 cant translate types
def dict_to_item(raw):
    if isinstance(raw, dict):
        return {
            'M': {
                k: dict_to_item(v) for k, v in raw.items()
            }
        }
    elif isinstance(raw, list):
        return {
            'L': [dict_to_item(v) for v in raw]
        }
    elif isinstance(raw, str):
        return {'S': raw}
    elif isinstance(raw, int):
        return {'N': str(raw)}

def get_ballot(ballot_date=None):
    if ballot_date is None:
        ballot_date = date.today()
    if isinstance(ballot_date, str):
        ballot_date = date.fromisoformat(ballot_date)

    q = {'KeyConditionExpression': 'id = :key AND ballot_date = :ballot_date',
         'Limit': 1, 'ScanIndexForward': True,
         'ExpressionAttributeValues': {':key': PKEY, ':ballot_date': ballot_date.isoformat()}}
    ballot_query = table.query(q)
    if not ballot_query.get('Count', 0):
        generate_ballot(table)
        ballot_query = table.query(q)
        assert ballot_query.get('Count', 0)
    return ballot_query.get('Items')[0]

def generate_ballot():
    ballot = table.query(KeyConditionExpression='id = :key',
                         Limit=1, ScanIndexForward=True,
                         ExpressionAttributeValues={':key': PKEY})

    if ballot.get('Count'):
        ballot_content = ballot.get('Items')[0]
    else:
        ballot_content = {}
        ballot_content['id'] = PKEY
        ballot_content['venues'] = {}

    ballot_content['votes'] = {}
    ballot_content['ballot_date'] = date.today().isoformat()
    table.put_item(Item=ballot_content)