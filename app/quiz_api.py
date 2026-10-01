from fsrs import Rating

from storage import get_definitions, add_review_event
from fsrs_service import review_word
from quiz import get_random_word, check_answer

CURRENT_USER_ID = 1

_VERDICT_TO_RATING = {
    "EQUIVALENT": Rating.Good,
    "PARTIAL (student answer is narrower/more specific)": Rating.Hard,
}


def get_quiz_question() -> dict:
    row, _definitions = get_random_word()
    return {"word_id": int(row["id"]), "word": row["word"]}


def submit_quiz_answer(word_id: int, answer: str) -> dict:
    definitions = get_definitions(word_id)

    verdict, correct = check_answer(answer, definitions)
    rating = _VERDICT_TO_RATING.get(verdict, Rating.Again)

    card, _review_log = review_word(CURRENT_USER_ID, word_id, rating)
    add_review_event(CURRENT_USER_ID, word_id, correct, "quiz")

    return {
        "verdict": verdict,
        "correct": correct,
        "fsrs_state": card.state.name,
        "stability": card.stability,
        "difficulty": card.difficulty,
        "next_review": card.due.isoformat() if card.due else None,
    }