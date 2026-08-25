from sentence_transformers import CrossEncoder
import torch
ENTAILMENT_THRESHOLD = 0.70
CONTRADICTION_THRESHOLD = 0.50


nli_model = CrossEncoder(
    "cross-encoder/nli-deberta-v3-base"
)

id2label= {
    index:label.lower()
    for index, label in nli_model.model.config.id2label.items()
}
label2idx={
    label:index 
    for index,label in id2label.items()
}
def predict_probs(premise, hypothesis):
    scores= nli_model.predict([(premise, hypothesis)])

    probs= torch.softmax(
        torch.tensor(scores),
        dim=1
    )[0]
    return {
        "entailment":probs[label2idx["entailment"]].item(),
        "neutral":probs[label2idx["neutral"]].item(),
        "contradiction":probs[label2idx["contradiction"]].item()
    }
def check_ans(correct_ans, student_ans):
    direction_a=predict_probs(premise=correct_ans, hypothesis=student_ans)
    direction_b=predict_probs(premise=student_ans, hypothesis=correct_ans)
    a_entails=(
        direction_a["entailment"]>=ENTAILMENT_THRESHOLD
    )
    b_entails=(
            direction_b["entailment"]>=ENTAILMENT_THRESHOLD
        )
    a_contradicts=(
        direction_a["contradiction"]>=CONTRADICTION_THRESHOLD
    )
    b_contradicts=(
            direction_b["contradiction"]>=CONTRADICTION_THRESHOLD
        )

    if a_contradicts or b_contradicts:
        verdict= "CONTRADICTION"
    elif a_entails and b_entails:
        verdict= "EQUIVALENT"
    elif a_entails and not b_entails:
        verdict = "PARTIAL (student answer is broader/vaguer)"

    elif b_entails and not a_entails:
        verdict = "PARTIAL (student answer is narrower/more specific)"

    else:
        verdict = "UNRELATED"
    return{
        "verdict":verdict,
        "direction_A":direction_a,
        "direction_B":direction_b

    }
quiz_cases = [

    {
        "note": "Exact paraphrase",

        "correct_answer":
            "The mitochondria is the powerhouse of the cell.",

        "student_answer":
            "Mitochondria produce energy for the cell."
    },

    {
        "note": "Student answer is too vague",

        "correct_answer":
            "Water boils at 100 degrees Celsius at sea level.",

        "student_answer":
            "Water boils at a certain temperature."
    },

    {
        "note": "Student answer is more specific",

        "correct_answer":
            "Paris is the capital of France.",

        "student_answer":
            "Paris, located on the Seine river, is the capital of France."
    },
    {
        "note": "Wrong answer",

        "correct_answer":
            "The Earth revolves around the Sun.",

        "student_answer":
            "The Sun revolves around the Earth."
    },

    {
        "note": "Completely unrelated",

        "correct_answer":
            "Photosynthesis converts sunlight into chemical energy.",

        "student_answer":
            "The stock market closed higher today."
    }
]
print("Label Mapping:",id2label)
for case in quiz_cases:
    result= check_ans(
        correct_ans=case["correct_answer"],
        student_ans=case["student_answer"]
    )
    print("\n" + "=" * 60)

    print("Note:")
    print(case["note"])

    print("\nCorrect answer:")
    print(case["correct_answer"])

    print("\nStudent answer:")
    print(case["student_answer"])

    print("\nVerdict:")
    print(result["verdict"])

    print("\nDirection A (correct -> student):")
    print(result["direction_A"])

    print("\nDirection B (student -> correct):")
    print(result["direction_B"])
