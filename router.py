# router.py — RA-only mode router
# Decides which RA mode should answer:
#   - outer_court   (chat / body)
#   - inner_court   (teaching / heart)
#   - holy_of_holies (judgement / brain)

def route_mode(message: str) -> str:
    """
    Decide which RA mode should answer this message.

    Returns one of:
      - "outer_court"
      - "inner_court"
      - "holy_of_holies"
    """
    m = (message or "").lower()

    # HOLY OF HOLIES — explicit judgement / law / verdict language
    if any(x in m for x in [
        "law", "mutemo", "verdict", "judgment", "judgement",
        "mutongo", "chisarudzo chenyu", "holy of holies",
        "curse", "blessing", "karma", "punish", "reward",
    ]):
        return "holy_of_holies"

    # INNER COURT — teaching, explanation, scroll curriculum, cosmology
    if any(x in m for x in [
        "teach", "explain", "how do i", "how to ",
        "factum probanda", "seal", "gate", "eclipse",
        "alphabet", "letters", "shona alphabet",
        "calendar", "karenda", "month", "gates of the year",
        "great zimbabwe", "spiral nation", "44 gates",
        "great year", "ages", "baba johani", "masowe",
    ]):
        return "inner_court"

    # HEART-PAIN still goes to judgement mode, but RA speaks
    if any(x in m for x in [
        "depressed", "heartbroken", "kurwadziwa", "kuchema",
        "anxiety", "lonely", "suicide", "ndiri kushungurudzika",
        "relationship", "marriage", "family problem",
    ]):
        return "holy_of_holies"

    # DEFAULT — simple RA chat in the Outer Court
    return "outer_court"