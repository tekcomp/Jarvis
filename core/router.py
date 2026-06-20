from core import commands

COMMANDS = [
    (["time"], commands.cmd_time),
    (["date", "today"], commands.cmd_date),
    (["joke"], commands.cmd_joke),
    (["capital"], commands.cmd_capital),
    (["hello", "hi"], commands.cmd_hello),
    (["weather"], commands.cmd_weather),
    (["news"], commands.cmd_news),
]


def route(text: str):
    text = text.lower()

    for keywords, func in COMMANDS:
        for k in keywords:
            if k in text:
                return func(text)

    return commands.cmd_fallback(text)