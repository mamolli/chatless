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
Here is a rundown of what I can do (simply write to me privately, or @mention me on the channel):
    `*add venue McDonaldos*` -> adds a new option for voting
    `*remove venue McDonaldos*` -> removes a new option for voting
    `*list venue*` -> shows all venues
    `*vote #2*` or `*vote McDonaldos*` -> cast vote for today's lunch
    `*show vote*` -> show current votes
"""
    return help_string

@chatless.match(r"add venue\s*(\S+)")
def add_venue(bot_event):
    dynamo.add_venue(bot_event['params'][0], bot_event['user'])
    ballot = dynamo.get_ballot()
    return ballot

def handle(event, context):
    assert SLACKBOT_OAUTH
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
