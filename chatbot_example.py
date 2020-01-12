import chatless

@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def default(bot_event):
    return "help shown here"

def handle(event, context):
    return chatless.handle(event)
