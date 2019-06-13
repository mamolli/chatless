import json
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



MAPPER = {
    r"hi": defunct,
    ('hi', 'hello', 'help', 'man', 'how'): defunct,
}
def extract_message(event):
    return json.loads(event['body'])['event']['text']
    
def handle(event, context):
    #print(json.dumps(event))
    # print(vars(context))
    print(extract_message(event))
    response = {'none': 'non'}
    return respond(STATUS_OK, response)

def handle_challenge_simple(body):
    response = {"challenge": json.loads(event['body'])['challenge']}

def route(message, mappings):


def respond(status, response_body):
    return {
        "statusCode": status,
        "body": json.dumps(response_body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": '*'
            },
        }

