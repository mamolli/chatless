import os
import chatless
import boto3

SLACKBOT_OAUTH = os.environ.get('SLACKBOT_OAUTH')
SLACK_URL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('votings')

@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    help_string = """
Aye mate, This is a simple lunch proposal/voting chat bot, written using chatless.
Here is a rundown of what I can do (simply write to me privately, or mention me on the channel):
    to add a new option for voting:
    *new venue [name of new venue]*
    _ie: new venue pizzahut_

    to vote on todays option
    *vote [name of venue | id number of venue]*
    _ie: vote mcdonalds_
    _ie: vote #4_
"""
    return help_string


def handle(event, context):
    assert SLACKBOT_OAUTH
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
