from sentence_transformers import CrossEncoder
import torch
nli_model = CrossEncoder(
    "cross-encoder/nli-deberta-v3-base"
)
print("Label Mapping:",nli_model.model.config.id2label)
test_cases = [
    {
    "type": "NEUTRAL",
    "premise": "The sky is blue.",
    "hypothesis": "There is a cloud in the sky."
    },
    {
        "type": "NEUTRAL",
        "premise": "The man is eating dinner.",
        "hypothesis": "The man owns a car."
    },
    {
        "type": "ENTAILMENT",
        "premise": "A dog is running in the park.",
        "hypothesis": "An animal is moving in the park."
    },
    {
        "type": "CONTRADICTION",
        "premise": "The dog is sleeping.",
        "hypothesis": "The dog is running."
    }
]
for case in test_cases:
    scores= nli_model.predict( [(case["premise"], case["hypothesis"])])
    prob = torch.softmax(
        torch.tensor(scores),
        dim=1
    )
    predicted_class= torch.argmax(
        prob,
        dim=1
    ).item()
    print("EXPECTED:", case["type"])
    print("Premise:", case["premise"])
    print("Hypothesis:", case["hypothesis"])

    print("Raw scores:", scores)

    print(
        "Probabilities:",
        prob.detach().numpy()
    )

    print("Predicted column:", predicted_class)