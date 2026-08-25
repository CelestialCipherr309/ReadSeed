import random
from storage import load_words, get_definitions,add_review_event
from semantic_check import check_best_match
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

def check_answer(user_ans,definitions):
    defn_texts= [meaning["definition"] for meaning in definitions]
    res=check_best_match(defn_texts, user_ans)
    print(res)
    return res["verdict"] in ACCEPTABLE_VERDICTS





def get_answer():
    row,definitions = get_random_word()
    word_id=int(row["id"])
    word=row["word"]
    

    print("\n Quiz Time!")
    print("Word:",word)

    answer= input("What does this word mean?")
    

    correct=check_answer(answer, definitions)

    if correct:
        print("Correct!")
        return word_id, True
    else:
        print("Not quite!")
        return word_id, False

def start_quiz(num_questions):
   score=0
   for i in range(num_questions):
       print(f"You are attempting question {i+1}/{num_questions}")

       word_id, was_correct = get_answer()

       if was_correct:
           score+=1

       add_review_event(
            CURRENT_USER_ID,
            word_id,
            was_correct,
            "quiz"
        )
   print("\nQuiz Finished.")
   print(f"Your score: {score}/{num_questions}")