import json
import router

STATUS_OK = 200

BOT_OAUTH = 'xoxb-648247024770-649400097058-IU3LgiXhMUBf3iXP8pytzBpM'
SLACK_URL = "https://slack.com/api/chat.postMessage"


# you can map a string -> by default interpret this as regexp or contains
# ???
# map over several words from tuple if any of matches

# example api
# @lunchbot hi/hello/help/man/how

# @lunchbot add venue
# creates venue name and adds #number
# -> returns a list of venues

# @lunchbot remove venue/number
# selfexplanatory
# -> returns a list of venues


# @lunchbot vote vanue/number
# only one vote per user
# -> returns current state of voting
# lunchbot: 
# 
# #4 KiK [votes: reksio, debil]

# TODO: make better abstractions

# Overall I think an interface of func(event) is probably the easiest one to handle
# event is simply a dict with detail about the environment, so regex matches etc
@router.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    print("showing help")
    return "siemano dziwko"


def handle(event, context):
    print("ROUTING YOLO")
    return router.handle_event(event, BOT_OAUTH, SLACK_URL)


