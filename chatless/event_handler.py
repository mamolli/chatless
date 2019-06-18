import json
import logging
import urllib.parse
import urllib.request
from pprint import pformat
from threading import Thread

from chatless import router

STATUS_OK = 200
STATUS_BAD = 504

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

def handle_thread(bot_event, bot_ouath, slack_url):
    if is_bot_message(bot_event):
        log.info('Ignoring messege from other bots.')
        return

    log.info("message received, nonbot")
    message, channel, user = extract_crucial(bot_event)
    source_event = {"m": message, "C": channel, "u": user}
    reply_message = router.route(message, user, channel)
    if reply_message:
        log.debug("Replying to channel %s, with message: %s", channel, reply_message)
        reply(reply_message, channel, bot_ouath, slack_url)
    else:
        log.debug("No reply for source event: %s", source_event)

# TODO: verify source
def simple_challenge(json_event):
    challenge = json_event.get('challenge')
    if challenge:
        return challenge
    return None

def handle_event(event, bot_ouath, slack_url):
    bot_event = load_body(event)
    challenge_phrase = simple_challenge(bot_event)
    if challenge_phrase:
        return respond(STATUS_OK, {"challenge": challenge_phrase})
    # rest of the code in thread
    # worker = Thread(target=handle_thread, args=[bot_event, bot_ouath, slack_url])
    # worker.start()
    handle_thread(bot_event, bot_ouath, slack_url)
    return respond(STATUS_OK, {})

def load_body(event):
    log.debug("extracting event body: %s", pformat(event))
    return json.loads(event.get('body'))
    # return json.loads(body.get('body'))

def is_bot_message(json_event):
    if json_event['event'].get('subtype') == "bot_message":
        return True
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
