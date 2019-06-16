import re
import logging
import urllib.parse
import urllib.request
import json

from pprint import pprint 

REGISTRY = []

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        # def fu(message=None, user=None, channel=None, *params):
        def fu(*args, **kwargs):
            return action(*args, **kwargs)
        # validate regex
        rx = validate_regex(regex)
        if rx:
            exec_pair = (rx, fu)
            REGISTRY.append(exec_pair)
        return fu
    return regex_deco


def validate_regex(regex):
    try:
        rx = re.compile(regex)
    except re.error:
        rx = None
    return rx

def route(message, user, channel):
    for regex, action in REGISTRY:
        m = re.search(regex, message)
        if m:
            params = m.groups()
            # inspect.signature(action).parameters.get('message')
            event = {
                'message': message,
                'user': user,
                'channel': channel,
                'params': params
                }
            values = action(bot_event=event)
            return values

#SECTION MOVED FROM CHATBOT

STATUS_OK = 200
STATUS_BAD = 504


def handle_event(event, bot_ouath, slack_url):
    json_event = load_event(event)
    log.debug(f"JSON EVENT received: {json_event}")
    if is_bot_message(json_event):
        log.info('Ignoring messege from other bots.')
        return
    log.info("message received, nonbot") 
    message, channel, user = extract_crucial(json_event)
    response = {"m": message, "C": channel, "u": user}
    reply_message = route(message, user, channel)
    if reply_message:
        reply("siemanko bot: {}".format(reply_message), channel, bot_ouath, slack_url)
    return respond(STATUS_OK, {"x": reply_message})

def load_event(event):
    body = json.loads(event['body'])    
    return json.loads(body.get('body'))

def is_bot_message(json_event):
    pprint(type(json_event))
    if json_event['event'].get('subtype') == "bot_message":
        return True
    print("not bot")
    return False

def extract_crucial(json_event):
    message = json_event['event'].get('text')
    channel = json_event['event'].get('channel')
    user = json_event['event'].get('user')
    return message, channel, user

    
def reply(message, channel, bot_ouath, slack_url):

    data = urllib.parse.urlencode(
        (
            ("token", bot_ouath),
            ("channel", channel),
            ("text", message)
        )
    )
    data = data.encode("ascii")
    
    # Construct the HTTP request that will be sent to the Slack API.
    request = urllib.request.Request(
        slack_url, 
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

def respond(status, response_body):
    return {
        "statusCode": status,
        "body": json.dumps(response_body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": '*'
            },
        }