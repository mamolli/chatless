import chatless

@chatless.default
@chatless.match(r"/hi|hello|man|help|docs/")
def show_help(bot_event):
    return "help shown here"


def handle(event, context):
    return chatless.handle(event)
