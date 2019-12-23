![](https://github.com/mamolli/chatless/workflows/ci/badge.svg) 
# Chatless - simple python3 aws lambda chatbot router
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


You need to install serverless framework and possibly aws-cli.
To follow-through:
`npm -g install serverless` and `pip3 install aws-cli` (remember to configure your aws-cli).

Create a directory, put in a bot.py file.
Temporarily we will include the package inside docker env, and copy the zippackage from inside the container to be later deployed using serverless.
