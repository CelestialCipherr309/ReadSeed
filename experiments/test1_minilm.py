from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def similarity(text1, text2):
    embedding1 = model.encode(
        text1,
        convert_to_tensor=True
    )

    embedding2 = model.encode(
        text2,
        convert_to_tensor=True
    )

    return util.cos_sim(embedding1, embedding2).item()


test_cases = [
    {
        "definition": "happy and cheerful",
        "correct": "very happy",
        "incorrect": "angry and upset"
    },
    {
        "definition": "a place where books are kept for people to read or borrow",
        "correct": "a place to borrow books",
        "incorrect": "a place where people buy food"
    },
    {
        "definition": "to move quickly on foot",
        "correct": "to run fast",
        "incorrect": "to sleep deeply"
    },
    {
        "definition": "very large in size or amount",
        "correct": "extremely big",
        "incorrect": "very small"
    },
    {
        "definition": "a feeling of fear or worry about something that may happen",
        "correct": "feeling scared about what might happen",
        "incorrect": "feeling completely relaxed"
    }
]


for case in test_cases:

    correct_score = similarity(
        case["definition"],
        case["correct"]
    )

    incorrect_score = similarity(
        case["definition"],
        case["incorrect"]
    )

    print("\nDefinition:", case["definition"])
    print("CORRECT:  ", round(correct_score, 4))
    print("INCORRECT:", round(incorrect_score, 4))