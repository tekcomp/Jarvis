import re


# =========================================================
# MAIN SCORER
# =========================================================
def score_conversation(user_input: str, response: str) -> dict:

    user_input = (user_input or "").lower()
    response = (response or "").lower()

    scores = {
        "relevance": relevance(user_input, response),
        "completeness": completeness(user_input, response),
        "clarity": clarity(response),
        "conciseness": conciseness(response),
        "naturalness": naturalness(response)
    }

    total = sum(scores.values()) / len(scores)

    return {
        "scores": scores,
        "total": round(total, 2)
    }


# =========================================================
# 1. RELEVANCE
# =========================================================
def relevance(user, resp):

    if not resp:
        return 0

    keywords = user.split()

    matches = sum(1 for k in keywords if k in resp)

    score = (matches / max(len(keywords), 1)) * 100

    return min(score, 100)


# =========================================================
# 2. COMPLETENESS
# =========================================================
def completeness(user, resp):

    if len(resp) < 5:
        return 10

    if "don't know" in resp or "not sure" in resp:
        return 50

    if len(resp.split()) > 20:
        return 90

    return 75


# =========================================================
# 3. CLARITY
# =========================================================
def clarity(resp):

    if not resp:
        return 0

    score = 100

    if resp.count("...") > 0:
        score -= 20

    if len(resp.split()) < 3:
        score -= 20

    return max(score, 0)


# =========================================================
# 4. CONCISENESS
# =========================================================
def conciseness(resp):

    words = len(resp.split())

    if words < 3:
        return 40

    if 5 <= words <= 25:
        return 95

    if words > 40:
        return 60

    return 80


# =========================================================
# 5. NATURALNESS
# =========================================================
def naturalness(resp):

    score = 80

    if resp.endswith("..."):
        score -= 20

    if "error" in resp:
        score -= 30