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
        "word": "bank",
        "definitions": [
            "the land alongside or sloping down to a river",
            "a financial institution that accepts deposits and provides loans",
            "to store money in a financial institution"
        ],
        "answer": "a financial institution where people keep their money"
    },

    {
        "word": "bright",
        "definitions": [
            "giving out or reflecting a lot of light",
            "intelligent and quick to learn",
            "cheerful and lively"
        ],
        "answer": "someone who is very intelligent"
    },

    {
        "word": "bark",
        "definitions": [
            "the outer covering of a tree",
            "the loud sound made by a dog"
        ],
        "answer": "the sound a dog makes"
    }
]


for case in test_cases:

    print("\n" + "=" * 60)
    print("WORD:", case["word"])
    print("ANSWER:", case["answer"])

    results = []

    for definition in case["definitions"]:

        score = similarity(
            definition,
            case["answer"]
        )

        results.append(
            (definition, score)
        )

    results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    for rank, (definition, score) in enumerate(results, start=1):

        print(f"\nRank {rank}")
        print("Definition:", definition)
        print("Similarity:", round(score, 4))