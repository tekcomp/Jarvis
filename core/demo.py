from core.command_registry import register

@register("demo_intro")
def demo_intro():
    return "Hi! I am Jarvis, your AI assistant. I can understand voice commands and respond in real time."

@register("demo_features")
def demo_features():
    return (
        "I can tell jokes, give time and date, "
        "and soon I will have memory and conversation awareness."
    )

@register("demo_fun")
def demo_fun():
    return "Try saying: tell me a joke, or what time is it."