import thefuzz.process
from thefuzz import fuzz

THRESHOLD = 90


def dedupe(entries):
    """
    Uses fuzzy matching to remove duplicate entries.
    """
    return thefuzz.process.dedupe(entries, THRESHOLD, fuzz.token_set_ratio)
