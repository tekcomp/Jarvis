from core.command_registry import register

@register("joke")
def joke():
    return "Why did the AI cross the road? To optimize the reward function."