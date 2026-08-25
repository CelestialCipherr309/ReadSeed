import random
from sentence_transformers import SentenceTransformer, CrossEncoder, util
import torch
MINILM_MIN_SIMILARITY=0.40
VERY_LOW_THRESHOLD = 0.30
NLI_ENTAILMENT_THRESHOLD=0.70
NLI_CONTRADICTION_THRESHOLD=0.50

_minilm_model = SentenceTransformer("all-MiniLM-L6-v2")
_nli_model = CrossEncoder("cross-encoder/nli-deberta-v3-base")

_id2label={
    index:label.lower()
    for index, label in _nli_model.model.config.id2label.items()

}
_label2idx={
    label: index
    for index, label in _id2label.items()
}
def _minilm_similarity(text_a:str, text_b:str)->float:
    embeddings=_minilm_model.encode([text_a, text_b], convert_to_tensor=True)
    return util.cos_sim(embeddings[0], embeddings[1]).item()
def _nli_predict_probs(premise:str, hypothesis:str)->dict:
    scores=_nli_model.predict([(premise, hypothesis)])
    probs= torch.softmax(
        torch.tensor(scores),
        dim=1
    )[0]
    return {
            "entailment":probs[_label2idx["entailment"]].item(),
            "neutral":probs[_label2idx["neutral"]].item(),
            "contradiction":probs[_label2idx["contradiction"]].item()
        }
_VERDICT_RANK = {
    "EQUIVALENT": 0,
    "PARTIAL (student answer is narrower/more specific)": 1,
    "PARTIAL (student answer is broader/vaguer)": 2,
    "UNRELATED": 3,
    "CONTRADICTION": 4,
}

def check_best_match(defn_candidates:list,student_ans:str)->dict:
    """
    We dont want that there are a lot of expensive checks so we will check the student_ans 
    with all the possible stored definitions and whichever one is most related , matlab
    the one with highest similarity score with the student answer will be picked and then
    NLI will be used on that so 3 checks by minilm(less expensive)
    and 1 check by NLI model this will optimize the situation.

    """
    if not defn_candidates:
        return {
            "verdict": "UNRELATED",
            "stage_used": "no definitions provided",
            "minilm_similarity": 0.0,
            "direction_A": None,
            "direction_B": None,
            "matched_definition": None,
        }
    #stage1(cheap): score every definition against the student ans
    similarities=[]
    for defn in defn_candidates:
        score= _minilm_similarity(defn,student_ans)
        similarities.append((defn, score))

    

    best_defn = None
    best_simi = None

    for defn, score in similarities:
        if best_simi is None or score > best_simi:
            best_simi = score
            best_defn = defn
        

        

    if best_simi<VERY_LOW_THRESHOLD:
        return {
            "verdict": "UNRELATED",
            "stage_used": "MiniLM only (best match still below threshold)",
            "minilm_similarity": best_simi,
            "direction_A": None,
            "direction_B": None,
            "matched_definition": best_defn,
        }
    qualifying=[]
    for defn, score in similarities:
        if score>=MINILM_MIN_SIMILARITY:
            qualifying.append((defn, score))

    if not qualifying:
        qualifying.append((best_defn, best_simi))




    
    #stage2(heavier) Apply NLI on the best match
    best_result=None
    best_rank=None
    best_defn_used=None

    for defn, score in qualifying:
        result= check_answer(
            defn,
            student_ans,
            similarity=score
        )

        rank=_VERDICT_RANK[result["verdict"]]
        if best_rank is None or rank<best_rank:
            best_rank=rank
            best_result= result
            best_defn_used=defn

    best_result["matched_definition"]= best_defn_used
    best_result["stage_used"] = (
    f"MiniLM -> NLI "
    f"(checked {len(qualifying)} qualifying definition(s))")
     

    return best_result



def check_answer(correct_answer:str, student_answer, similarity=None)->dict:
    if similarity is None:
        similarity= _minilm_similarity(correct_answer, student_answer)
    if similarity<MINILM_MIN_SIMILARITY:
        return {
            "verdict": "UNRELATED",
            "stage_used": "MiniLM only (rejected before NLI)",
            "minilm_similarity": similarity,
            "direction_A": None,
            "direction_B": None,
        }
    direction_a = _nli_predict_probs(premise=correct_answer, hypothesis=student_answer)
    direction_b = _nli_predict_probs(premise=student_answer, hypothesis=correct_answer)
 
    a_entails = direction_a["entailment"] >= NLI_ENTAILMENT_THRESHOLD
    b_entails = direction_b["entailment"] >= NLI_ENTAILMENT_THRESHOLD
    a_contradicts = direction_a["contradiction"] >= NLI_CONTRADICTION_THRESHOLD
    b_contradicts = direction_b["contradiction"] >= NLI_CONTRADICTION_THRESHOLD
 
    if a_contradicts or b_contradicts:
        verdict = "CONTRADICTION"
    elif a_entails and b_entails:
        verdict = "EQUIVALENT"
    elif a_entails and not b_entails:
        verdict = "PARTIAL (student answer is broader/vaguer)"
    elif b_entails and not a_entails:
        verdict = "PARTIAL (student answer is narrower/more specific)"
    else:
        verdict = "UNRELATED"
 
    return {
        "verdict": verdict,
        "stage_used": "MiniLM -> NLI",
        "minilm_similarity": similarity,
        "direction_A": direction_a,
        "direction_B": direction_b,
    }