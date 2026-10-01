import pandas as pd
from fastapi import FastAPI, HTTPException
from schemas import (
    WordLookupRequest, WordLookupResponse,
    WordConfirmRequest, WordConfirmResponse,
    RelatedWordsResponse, AddRelatedWordsRequest, AddRelatedWordsResponse,
    QuizQuestionResponse, QuizAnswerRequest, QuizAnswerResponse,
)

from storage import load_words
import learn_api
import quiz_api

app=FastAPI(title="ReadSeed API")
#------words----------
@app.post("/words/lookup", response_model=WordLookupResponse)
def lookup_word(payload:WordLookupRequest):
    try:
        return learn_api.lookup_word(payload.word)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/words/confirm",response_model=WordConfirmResponse)
def confirm_word(payload:WordConfirmRequest):
    try:
        word_id=learn_api.confirm_add_word(payload.word,payload.meanings)
        return  {
            "word_id":word_id,
            "message":"Word Added Successfully"
        }
    except Exception as exc:
        raise HTTPException(status_code=500,detail=str(exc))

@app.get("/words")
def list_words():
    try:
        df=load_words()
        return df.where(pd.notnull(df),None).to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
@app.get("/words/related", response_model=RelatedWordsResponse)
def related_words(word:str):
    try:
        return learn_api.get_related_words_for(word)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/words/related/add",response_model=AddRelatedWordsResponse)
def add_related_words(payload:AddRelatedWordsRequest):
    try:
        return learn_api.add_related_words(payload.words)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

#-----quiz------
@app.get("/quiz/question", response_model=QuizQuestionResponse)
def quiz_question():
    try:
        return quiz_api.get_quiz_question()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
 
 
@app.post("/quiz/answer", response_model=QuizAnswerResponse)
def quiz_answer(payload: QuizAnswerRequest):
    try:
        return quiz_api.submit_quiz_answer(payload.word_id, payload.answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
 
