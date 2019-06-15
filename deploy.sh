#!/bin/bash
set -e
serverless deploy
curl -d "@test/chat-msg.json" -X POST https://7gr5oewmhh.execute-api.us-east-1.amazonaws.com/dev/chat
