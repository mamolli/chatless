import os
import chatless

SLACKBOT_OAUTH = os.environ.get('SLACKBOT_OAUTH')
SLACK_URL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"


@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    return "siemano"


def handle(event, context):
    assert SLACKBOT_OAUTH
    return chatless.handle(event, SLACKBOT_OAUTH, SLACK_URL)
