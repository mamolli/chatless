import os
import json
import logging
import urllib.parse
import urllib.request
from pprint import pformat

import boto3
from chatless import router

STATUS_OK = 200

ENV_OAUTH = os.environ.get('SLACKBOT_OAUTH')
ENV_SLACKURL = os.environ.get('SLACK_URL') or "https://slack.com/api/chat.postMessage"

SQS_URL = os.environ.get('SQS_QUEUE')

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.DEBUG)

def handle_message(bot_event, bot_ouath, slack_url):
    # TODO: integration testing may require bot to bot communication
    if is_bot_message(bot_event):
        log.info('Ignoring message from other bots.')
        return
    log.info("message received, nonbot - preparing reply")
    message, channel, user = extract_message_data(bot_event)
    reply_message = router.route(message, user, channel) or "Could not find a proper answer"
    log.debug("Replying to channel %s, with message: %s", channel, reply_message)
    reply(reply_message, channel, bot_ouath, slack_url)

# TODO: verify source later
def simple_challenge(json_event):
    challenge = json_event.get('challenge')
    if challenge:
        return challenge
    return None


def handle(event, bot_ouath=ENV_OAUTH, slack_url=ENV_SLACKURL):
    sqs = boto3.client('sqs')
    # naively guessing having 'Record' means sqs
    sqs_event = next(iter(event.get('Records', [])), None)
    bot_event = body_to_json(sqs_event or event)

    # check if its just verification from initial slack run
    challenge_phrase = simple_challenge(bot_event)
    if challenge_phrase:
        # just reply and abort, its not meaningful
        return respond(STATUS_OK, {"challenge": challenge_phrase})

    if sqs_event:
        # process request from queue
        # TODO: support for DLQueue
        sqs.delete_message(QueueUrl=SQS_URL, ReceiptHandle=sqs_event.get("receiptHandle"))
        handle_message(bot_event, bot_ouath, slack_url)
    else:
        sqs.send_message(QueueUrl=SQS_URL, MessageBody=json.dumps(bot_event))
    
    # in general, if we got ok data, we reply all went well, otherwise slack will retry
    return respond(STATUS_OK, {})

def body_to_json(event):
    body = json.loads(event.get('body'))
    return body
    # return json.loads(body.get('body'))

def is_bot_message(slack_event):
    if slack_event['event'].get('subtype') == "bot_message":
        return True
    return False

def extract_message_data(slack_event):
    message = slack_event['event'].get('text')
    channel = slack_event['event'].get('channel')
    user = slack_event['event'].get('user')
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
