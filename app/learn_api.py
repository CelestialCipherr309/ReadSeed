from storage import find_word, get_definitions, save_word, add_user_word
from dictionary import get_meaning
from datamuse_api import get_related_words
from spellcheck import suggest_words

CURRENT_USER_ID = 1


def lookup_word(word: str) -> dict:
    """Look up a word: already-learned, found in dictionary, spelling
    suggestion, or not found at all. Mirrors the branching in main.py's
    choice == "1" block, minus the input()/print() calls."""

    existing = find_word(word)
    if existing is not None:
        meanings = get_definitions(existing["id"])
        return {
            "status": "existing",
            "word": existing["word"],
            "word_id": existing["id"],
            "meanings": meanings,
        }

    meanings = get_meaning(word)
    if meanings is not None:
        return {"status": "found", "word": word, "meanings": meanings}

    suggested_word, score = suggest_words(word)
    if suggested_word is None:
        return {"status": "not_found"}

    return {"status": "suggestion", "suggested_word": suggested_word, "score": score}


def confirm_add_word(word: str, meanings: list) -> int:
    """Actually save a word + its meanings and attach it to the current
    user. Equivalent to the DB part of add_word_and_show(), without the
    print()s or the interactive offer_related_words() call."""

    meanings_as_dicts = [dict(m) for m in meanings]
    word_id = save_word(word, meanings_as_dicts)
    add_user_word(CURRENT_USER_ID, word_id)
    return word_id


def get_related_words_for(word: str) -> dict:
    """Fetch synonyms/antonyms for a word. Equivalent to the data-fetching
    half of offer_related_words(), without the input() prompts."""

    related = get_related_words(word)
    return {
        "word": word,
        "synonyms": related["synonyms"],
        "antonyms": related["antonyms"],
    }


def add_related_words(words: list) -> dict:
    """Add a batch of chosen related words (synonyms/antonyms the user
    picked). Equivalent to the loop in offer_related_words() that calls
    learn_related_words() for each accepted word, minus the input()s."""

    added, already_had, skipped = [], [], []

    for word in words:
        existing = find_word(word)
        if existing is not None:
            add_user_word(CURRENT_USER_ID, existing["id"])
            already_had.append(word)
            continue

        meanings = get_meaning(word)
        if meanings is None:
            skipped.append(word)
            continue

        word_id = save_word(word, meanings)
        add_user_word(CURRENT_USER_ID, word_id)
        added.append(word)

    return {
        "added": added,
        "already_had": already_had,
        "skipped_no_definition": skipped,
    }