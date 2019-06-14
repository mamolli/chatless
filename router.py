import re
import urllib.parse
import urllib.request
import json

REGISTRY = []

# avoid OOP at all costs
def match(regex):
    def regex_deco(action):
        def fu(message=None, user=None, channel=None, *params):
            return action(message, user, channel, *params)
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
            values = action(message, user, channel, *params)
            return values

#SECTION MOVED FROM CHATBOT

STATUS_OK = 200
STATUS_BAD = 504


def handle_event(event, bot_ouath, slack_url):
    json_event = load_event(event)
    if is_bot_message(json_event):
        return 
    message, channel, user = extract_crucial(json_event)
    response = {"m": message, "C": channel, "u": user}
    reply_message = route(message, user, channel)
    reply("siemanko bot: {}".format(reply_message), channel, bot_ouath, slack_url)

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

    
def reply(message, channel, bot_ouath, slack_url):
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
