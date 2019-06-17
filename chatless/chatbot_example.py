import json
import chatless

BOT_OAUTH = 'xoxb-648247024770-666706406096-RzX2wOfHYNFqX0nTMqd3yulN' 
SLACK_URL = "https://slack.com/api/chat.postMessage"


@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    print("showing help")
    return "siemano dziwko"


def handle(event, context):
    return chatless.handle(event, BOT_OAUTH, SLACK_URL)


