import random

from storage import load_words, get_definitions, add_review_event
from semantic_check import check_best_match
from fsrs import Rating
from fsrs_service import review_word


CURRENT_USER_ID = 1

ACCEPTABLE_VERDICTS = {
    "EQUIVALENT",
    "PARTIAL (student answer is narrower/more specific)",
}


def get_random_word():
    df = load_words()
    row = df.sample(1).iloc[0]

    definitions = get_definitions(int(row["id"]))

    return row, definitions


def check_answer(user_ans, definitions):
    defn_texts = [meaning["definition"] for meaning in definitions]

    res = check_best_match(defn_texts, user_ans)

    print(res)

    verdict = res["verdict"]

    correct = verdict in ACCEPTABLE_VERDICTS

    return verdict, correct


def get_answer():
    row, definitions = get_random_word()

    word_id = int(row["id"])
    word = row["word"]

    print("\nQuiz Time!")
    print("Word:", word)

    answer = input("What does this word mean? ")

    verdict, correct = check_answer(answer, definitions)

    if correct:
        print("Correct!")
    else:
        print("Not quite!")

    # Convert semantic result → FSRS rating
    if verdict == "EQUIVALENT":
        rating = Rating.Good

    elif verdict == "PARTIAL (student answer is narrower/more specific)":
        rating = Rating.Hard

    else:
        rating = Rating.Again

    return word_id, correct, rating


def start_quiz(num_questions):
    score = 0

    for i in range(num_questions):

        print(f"\nYou are attempting question {i + 1}/{num_questions}")

        word_id, was_correct, rating = get_answer()

        if was_correct:
            score += 1

        # Update FSRS state in PostgreSQL
        card, review_log = review_word(
            CURRENT_USER_ID,
            word_id,
            rating
        )

        # Save quiz attempt history
        add_review_event(
            CURRENT_USER_ID,
            word_id,
            was_correct,
            "quiz"
        )

        print("FSRS State:", card.state)
        print("FSRS Stability:", card.stability)
        print("FSRS Difficulty:", card.difficulty)
        print("Next Review:", card.due)

    print("\nQuiz Finished.")
    print(f"Your score: {score}/{num_questions}")


if __name__ == "__main__":
    print("===== FSRS QUIZ INTEGRATION TEST =====")

    # Test word
    word_id = 1

    # Test answer
    user_answer = "a feeling of being very happy"

    # Get definitions
    definitions = get_definitions(word_id)

    print("\nDefinitions:")
    for definition in definitions:
        print("-", definition["definition"])

    # Check semantic answer
    verdict, correct = check_answer(user_answer, definitions)

    print("\nSemantic Result:")
    print("Verdict:", verdict)
    print("Correct:", correct)

    # Convert verdict to FSRS rating
    if verdict == "EQUIVALENT":
        rating = Rating.Good

    elif verdict == "PARTIAL (student answer is narrower/more specific)":
        rating = Rating.Hard

    else:
        rating = Rating.Again

    print("FSRS Rating:", rating)

    # Send to FSRS
    card, review_log = review_word(
        CURRENT_USER_ID,
        word_id,
        rating
    )

    print("\n===== FSRS RESULT =====")
    print("State:", card.state)
    print("Step:", card.step)
    print("Stability:", card.stability)
    print("Difficulty:", card.difficulty)
    print("Due:", card.due)

    print("\n===== TEST PASSED =====")