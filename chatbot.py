import json
import re
import enum
import urllib.request 
import urllib.parse

import router

STATUS_OK = 200
STATUS_BAD = 504

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
def show_help():
    print("showing help")
    return "siemano dziwko"

def load_event(event):
    body = json.loads(event['body'])    
    return body

def is_bot_message(json_event):
    if json_event['event'].get('subtype') == "bot_message":
        return True
    return False

def extract_crucial(json_event):
    message = json_event['event']['text']
    channel = json_event['event']['channel']
    user = json_event['event']['user']
    return message, channel, user

    
def reply(message, channel):
    data = urllib.parse.urlencode(
        (
            ("token", BOT_OAUTH),
            ("channel", channel),
            ("text", message)
        )
    )
    data = data.encode("ascii")
    
    # Construct the HTTP request that will be sent to the Slack API.
    request = urllib.request.Request(
        SLACK_URL, 
        data=data, 
        method="POST"
    )
    # Add a header mentioning that the text is URL-encoded.
    request.add_header(
        "Content-Type", 
        "application/x-www-form-urlencoded"
    )
    
    # Fire off the request!
    urllib.request.urlopen(request).read()

def handle(event, context):
    print(json.dumps(event))
    # print(vars(context))

    json_event = load_event(event)
    if is_bot_message(json_event):
        return respond(STATUS_OK, {"allgood": "ok"})
    message, channel, user = extract_crucial(json_event)
    response = {"m": message, "C": channel, "u": user}
    reply("siemanko bot: {}".format(message), channel)
    return respond(STATUS_OK, response)

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

