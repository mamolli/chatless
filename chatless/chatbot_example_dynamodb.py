import os
from datetime import date
import boto3
import logging
# from boto3.dynamodb.conditions import Key, Attr
import chatless
from chatless import dynamo

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

SLACKBOT_OAUTH = os.environ.get('SLACKBOT_OAUTH')
SLACK_URL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"

@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    help_string = """\
Aye mate, This is a simple lunch proposal/voting chat bot, written using chatless.
Here is a rundown of what I can do (simply write *direct message or @mention me* on the channel):
    *`add place McDonaldos`* -> adds a new option for voting
    *`remove place McDonaldos`* -> removes a new option for voting
    *`show place`* -> shows all places
    *`vote $2`* or *`vote McDonaldos`* -> cast vote for today's lunch
    *`show vote`* -> show current votes
"""
    return help_string

@chatless.match(r"show\s*places?\s*")
def show_place(bot_event):
    ballot = dynamo.get_ballot()
    places = (f"_${v['id']}_ *{v['name']}*" for v in ballot['places'])
    places_str = '\n\t'.join(places)
    out = f"Here is the list of all vevnues:\n\t{places_str}"
    return out

@chatless.match(r"add\s*place\s*(\S+.*)")
def add_place(bot_event):
    dynamo.add_place(bot_event['params'][0], bot_event['user'])
    ballot = dynamo.get_ballot()
    places = (f"_${v['id']}_ *{v['name']}*" for v in ballot['places'])
    places_str = '\n\t'.join(places)
    out = f"Place added, here is the updated list of all vevnues:\n\t{places_str}"
    return out

@chatless.match(r"remove\s*place\s*(\S+.*)")
def remove_place(bot_event):
    dynamo.remove_place(bot_event['params'][0])
    ballot = dynamo.get_ballot()
    places = (f"_${v['id']}_ *{v['name']}*" for v in ballot['places'])
    places_str = '\n\t'.join(places)
    out = f"Place removed, here is the updated list of all vevnues:\n\t{places_str}"
    return out

@chatless.match(r"vote\s*(\S+.*)")
def add_vote(bot_event):
    dynamo.add_vote(bot_event['params'][0], bot_event['user'])
    ballot = dynamo.get_ballot()
    votes_count = {}
    log.debug("Ballot state %s", ballot)
    # transpose vote dict
    for u, p in ballot['votes'].items():
        votes_count[p['name']] = votes_count.get(p['name'], {})
        votes_count[p['name']]['count'] = votes_count[p['name']].get('count', 0) + 1
        if not votes_count[p['name']].get('users'):
            votes_count[p['name']]['users'] = set()
        votes_count[p['name']]['users'].add(u)
    votes = (f"*{k}* : *{p['count']} votes*" for k, p in votes_count.items())
    votes_str = "\n\t".join(votes)
    out = f"Vote added, voting results currently look like this: \n\t {votes_str}"
    return out

@chatless.match(r"show\s+votes?\s*")
def show_vote(bot_event):
    ballot = dynamo.get_ballot()
    votes_count = {}
    for u, p in ballot['votes'].items():
        votes_count[p['name']] = votes_count.get(p['name'], {})
        votes_count[p['name']]['count'] = votes_count[p['name']].get('count', 0) + 1
        if not votes_count[p['name']].get('users'):
            votes_count[p['name']]['users'] = set()
        votes_count[p['name']]['users'].add(u)
    log.info("Votes results look like %s", votes_count)
    votes = []
    for k, v in votes_count.items():
        users = (f"<@{u}>"for u in v['users'])
        users = ", ".join(users)
        vote_str = f"*{k}* : *{v['count']} votes by: {users}*"
        votes.append(vote_str)
    # votes = (f"*{k}* : *{v['count']} votes by: {users}*" for k, v in votes_count.items())
    votes_str = "\n\t".join(votes)
    if not len(votes_count):
        votes_str = "*No votes yet*, try voting like this: *`vote RestaurantName`* or *`vote $1`*"
    out = f"voting results currently look like this: \n\t {votes_str}"
    return out

def handle(event, context):
    assert SLACKBOT_OAUTH
    log.info("EVENT receive: %s \n CONTEXT: %s", event, context)
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
