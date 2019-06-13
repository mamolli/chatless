import json
import re
import enum

STATUS_OK = 200
STATUS_BAD = 504


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

def show_help():
    print("showing help")

def add_venue():
    print("adding venue")

def add_vote():
    print("adding vote")

PARSE = { 
    r'add (\S+)': add_venue,
    r'vote (\S+)': add_vote,
    r'/hi|hello|man|help|how/': show_help,
    []: show_help
 }

def route(message, parse_map):
    for parse_map_item in parse_map.items():
        rex, fmap = parse_map_item 
        print(re.findall(rex, message))

def extract_message(event):
    return json.loads(event['body'])['event']['text']
    
def handle(event, context):
    #print(json.dumps(event))
    # print(vars(context))
    message = extract_message(event)
    response = {'none': 'non'}
    route(message, PARSE)
    return respond(STATUS_OK, response)

def handle_challenge_simple(body):
    response = {"challenge": json.loads(event['body'])['challenge']}

def respond(status, response_body):
    return {
        "statusCode": status,
        "body": json.dumps(response_body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": '*'
            },
        }

