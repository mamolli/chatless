# Chatless - chatbot router-framework for slack, python3 & AWS-Lambda

## Quickstart

For your first bot you basically need 2 files.
* `bot.py` -> your simple bot
* `serverless.yaml` -> your serverless config file

### `bot.py`
```
import chatless

@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    return "hi man"

def handle(event, context):
    return chatless.handle(event)

```

Basically you need one function bound to your lambda.
See `serverless.yaml` to see a simple setup.
This function `def handle(event, context):` is basically your lambdas app entry point.
The other function(s) are decorated with regexp expressions and should take in one parameter `bot_event`.
* decorator `@chatless.match(r"something")` tries to match expression and passes matching groups in first parameter.
* decorator `@chatless.default` marks a function to be used as default if no matches are found

### `serverless.yaml.example`
```
service: chatbot-serverless

frameworkVersion: ">=1.2.0 <2.0.0"

custom:
  app_name: Example
  dynamo_name: ${self:custom.app_name}-dynamo
  sqs_name: ${self:custom.app_name}-sqs


provider:
  name: aws
  runtime: python3.6 # python3.7 has bad support, due to incorrect log handling
  memorySize: 128
  environment:
    DYNAMODB_TABLE: ${self:custom.dynamo_name}
  iamRoleStatements:
    - Effect: Allow
      Action:
      - sqs:DeleteMessage
      - sqs:ReceiveMessage
      - sqs:SendMessage
      - sqs:SendMessageBatch
      Resource: "arn:aws:sqs:*:*:${self:custom.sqs_name}" 
    - Effect: Allow
      Action:
        - dynamodb:Query
        - dynamodb:Scan
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
      Resource: "arn:aws:dynamodb:${opt:region, self:provider.region}:*:table/${self:provider.environment.DYNAMODB_TABLE}"

resources:
  Resources:
    Messages:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.sqs_name}
        MessageRetentionPeriod: 12000
        VisibilityTimeout: 60
    LuncherbotDynamoDbTable:
      Type: AWS::DynamoDB::Table
      DeletionPolicy: Delete
      Properties:
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
          - AttributeName: sortkey
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
          - AttributeName: sortkey
            KeyType: RANGE
        ProvisionedThroughput:
          ReadCapacityUnits: 1
          WriteCapacityUnits: 1
        TableName: ${self:provider.environment.DYNAMODB_TABLE}

functions:
  chatbot:
    handler: chatless.chatbot_example_dynamodb.handle
    environment:
      SLACKBOT_OAUTH: ${file(./secrets.yaml):SLACKBOT_OAUTH}
      PROVIDER_REGION: "${self:provider.region}"
      DYNAMODB_TABLE: "${self:provider.environment.DYNAMODB_TABLE}"
      SQS_QUEUE:
        Ref: Messages
    events:
      - http:
          path: chat
          method: post
      - sqs:
          arn:
            Fn::GetAtt:
              - Messages
              - Arn

```
You need to install serverless framework and possibly aws-cli.
To follow-through:
`npm -g install serverless` and `pip3 install aws-cli` (remember to configure your aws-cli).

Create a directory, put in a bot.py file.
Temporarily we will include the package inside docker env, and copy the zippackage from inside the container to be later deployed using serverless.