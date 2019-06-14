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

@router.match(r"/hi|hello|man|help|docs/")
def show_help(message, user, channel):
    print("showing help")
    return "siemano dziwko"


def handle(event, context):
    print(json.dumps(event))
    # print(vars(context))
    router.handle_event(event, BOT_OAUTH, SLACK_URL)
    return respond(STATUS_OK, {"x": "x"})

# def handle_challenge_simple(body):
    # response = {"challenge": json.loads(event['body'])['challenge']}

def respond(status, response_body):
    return {
        "statusCode": status,
        "body": json.dumps(response_body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": '*'
            },
        }

