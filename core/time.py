from datetime import datetime
from core.command_registry import register

@register("time")
def time_cmd():
    return f"The time is {datetime.now().strftime('%H:%M')}."