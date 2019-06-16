import json
import logging
import router
import urllib.parse
import urllib.request
from pprint import pformat

STATUS_OK = 200
STATUS_BAD = 504

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)


# TODO: verify source
def simple_challenge(json_event):
    challenge = json_event.get('challenge')
    if challenge:
        return challenge
    return None

def handle_event(event, bot_ouath, slack_url):
    bot_event = load_body(event)
    # simple challenge reply for bot verification    
    challenge_phrase = simple_challenge(bot_event)
    if challenge_phrase:
        return respond(STATUS_OK, {"challenge": challenge_phrase})

    #print(json_event.keys())
    # bot_event = load_body(json_event)
    # log.debug(f"JSON EVENT received: {bot_event}")
    if is_bot_message(bot_event):
        log.info('Ignoring messege from other bots.')
        return
    log.info("message received, nonbot") 
    message, channel, user = extract_crucial(bot_event)
    response = {"m": message, "C": channel, "u": user}
    reply_message = router.route(message, user, channel)
    if reply_message:
        log.debug("Replying to channel %s, with message: %s", channel, reply_message)
        reply("siemanko bot: {}".format(reply_message), channel, bot_ouath, slack_url)
    return respond(STATUS_OK, {"text": reply_message, "channel": channel})

def load_body(event):
    log.debug("extracting event body: %s", pformat(event))
    return json.loads(event.get('body'))    
    # return json.loads(body.get('body'))

def is_bot_message(json_event):
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
