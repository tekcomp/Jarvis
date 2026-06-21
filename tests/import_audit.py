import os

BANNED_STRINGS = [
    "from core.brain import",
    "import core.brain",
]


def scan_files():
    violations = []

    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()

                    for ban in BANNED_STRINGS:
                        if ban in content:
                            violations.append((path, ban))

    if violations:
        raise RuntimeError(f"IMPORT VIOLATIONS FOUND: {violations}")


if __name__ == "__main__":
    scan_files()