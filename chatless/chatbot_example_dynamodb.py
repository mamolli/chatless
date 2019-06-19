import os
from datetime import date
import boto3
# from boto3.dynamodb.conditions import Key, Attr
import chatless
from chatless import dynamo

SLACKBOT_OAUTH = os.environ.get('SLACKBOT_OAUTH')
SLACK_URL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"


@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    help_string = """\
Aye mate, This is a simple lunch proposal/voting chat bot, written using chatless.
Here is a rundown of what I can do (simply write *direct message or @mention me* on the channel):
    *`add venue McDonaldos`* -> adds a new option for voting
    *`remove venue McDonaldos`* -> removes a new option for voting
    *`show venue`* -> shows all venues
    *`vote $2`* or *`vote McDonaldos`* -> cast vote for today's lunch
    *`show vote`* -> show current votes
"""
    return help_string

@chatless.match(r"show\s*venues?\s*")
def show_venue(bot_event):
    ballot = dynamo.get_ballot()
    venues = (f"#{v['id']} {v['name']}" for v in ballot['venues'])
    venues_str = '\n\t'.join(venues)
    out = f"Here is the list of all vevnues:\n\t{venues_str}"
    return out

@chatless.match(r"add\s*venue\s*(\S+)")
def add_venue(bot_event):
    dynamo.add_venue(bot_event['params'][0], bot_event['user'])
    ballot = dynamo.get_ballot()
    venues = (f"${v['id']} {v['name']}" for v in ballot['venues'])
    venues_str = '\n\t'.join(venues)
    out = f"Venue added, here is the updated list of all vevnues:\n\t{venues_str}"
    return out

@chatless.match(r"remove\s*venue\s*(\S+)")
def remove_venue(bot_event):
    dynamo.remove_venue(bot_event['params'][0])
    ballot = dynamo.get_ballot()
    venues = (f"${v['id']} {v['name']}" for v in ballot['venues'])
    venues_str = '\n\t'.join(venues)
    out = f"Venue added, here is the updated list of all vevnues:\n\t{venues_str}"
    return out

@chatless.match(r"vote\s*(\S+)")
def add_vote(bot_event):
    dynamo.add_vote(bot_event['params'][0], bot_event['user'])
    ballot = dynamo.get_ballot()
    votes_count = {}
    for u, v in ballot['votes'].items():
        print(v['name'])
        votes_count[v['name']] = votes_count.get(v['name'], {})
        votes_count[v['name']]['count'] = votes_count[v['name']].get('count', 0) + 1
        if not votes_count[v['name']].get('users'):
            votes_count[v['name']]['users'] = set()
        votes_count[v['name']]['users'].add(u)
    votes = (f"*{k}* : *{v['count']} votes*" for k, v in votes_count.items())
    votes_str = "\n\t".join(votes)
    out = f"Vote added, voting results currently look like this: \n\t {votes_str}"
    return out

@chatless.match(r"show\s+votes?\s*")
def show_vote(bot_event):
    ballot = dynamo.get_ballot()
    votes_count = {}
    for u, v in ballot['votes'].items():
        print(v['name'])
        votes_count[v['name']] = votes_count.get(v['name'], {})
        votes_count[v['name']]['count'] = votes_count[v['name']].get('count', 0) + 1
        if not votes_count[v['name']].get('users'):
            votes_count[v['name']]['users'] = set()
        votes_count[v['name']]['users'].add(u)
    votes = (f"*{k}* : *{v['count']} votes*" for k, v in votes_count.items())
    votes_str = "\n\t".join(votes)
    out = f"voting results currently look like this: \n\t {votes_str}"
    return out

def handle(event, context):
    assert SLACKBOT_OAUTH
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
