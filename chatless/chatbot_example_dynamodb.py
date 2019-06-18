import os
from datetime import date
import boto3
# from boto3.dynamodb.conditions import Key, Attr
import chatless

SLACKBOT_OAUTH = os.environ.get('SLACKBOT_OAUTH')
SLACK_URL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"


@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    help_string = """\
Aye mate, This is a simple lunch proposal/voting chat bot, written using chatless.
Here is a rundown of what I can do (simply write to me privately, or mention me on the channel):
    to add a new option for voting:
    *new venue [name of new venue]*
    _ie: new venue pizzahut_

    to vote on today's option
    *vote [name of venue | id number of venue]*
    _ie: vote mcdonalds_
    _ie: vote #4_
    *show vote*
    *show venues*
"""
    return help_string


def handle(event, context):
    assert SLACKBOT_OAUTH
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
