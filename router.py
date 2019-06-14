import re

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
