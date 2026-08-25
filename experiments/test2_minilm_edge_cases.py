from sentence_transformers import SentenceTransformer, util
model =SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)
def similarity(t1,t2):
    embedding1= model.encode(
        t1,convert_to_tensor=True
    )
    embedding2= model.encode(
            t2,convert_to_tensor=True
        )
    return util.cos_sim(embedding1, embedding2).item()

test_cases = [

    
    {
        "type": "Synonym",
        "definition": "very happy",
        "answer": "joyful"
    },

    
    {
        "type": "Paraphrase",
        "definition": "to move quickly on foot",
        "answer": "to run fast"
    },

    
    {
        "type": "Antonym",
        "definition": "very large in size",
        "answer": "very small"
    },

    
    {
        "type": "Related but incorrect",
        "definition": "a place where books are kept for people to read or borrow",
        "answer": "a place where books are sold"
    },

    {
        "type": "Same topic, wrong meaning",
        "definition": "a person who treats sick animals",
        "answer": "a person who treats sick people"
    },

   
    {
        "type": "Partial answer",
        "definition": "a feeling of fear or worry about something that may happen",
        "answer": "fear"
    },

   
    {
        "type": "Very short answer",
        "definition": "lasting for a very short time",
        "answer": "temporary"
    },

    {
        "type": "Negation",
        "definition": "someone who is willing to help others",
        "answer": "someone who is not willing to help others"
    },

    {
        "type": "Unrelated",
        "definition": "lasting for a very short time",
        "answer": "a blue car"
    },

   
    {
        "type": "Correct paraphrase",
        "definition": "a person who is extremely careful about details",
        "answer": "someone who pays very close attention to small details"
    }
]
for case in test_cases:
    score= similarity(
        case["definition"],
        case["answer"]
    )
    print("\nType:", case["type"])
    print("Definition:", case["definition"])
    print("Answer:", case["answer"])
    print("Similarity:", round(score, 4))
   