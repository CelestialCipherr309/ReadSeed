from typing import List, Optional
from pydantic import BaseModel


class Meaning(BaseModel):
    part_of_speech: str
    definition: str


class WordLookupRequest(BaseModel):
    word: str


class WordLookupResponse(BaseModel):
    status: str  # "existing" | "found" | "suggestion" | "not_found"
    word: Optional[str] = None
    word_id: Optional[int] = None
    meanings: Optional[List[Meaning]] = None
    suggested_word: Optional[str] = None
    score: Optional[float] = None


class WordConfirmRequest(BaseModel):
    word: str
    meanings: List[Meaning]


class WordConfirmResponse(BaseModel):
    word_id: int
    message: str


class RelatedWordsResponse(BaseModel):
    word: str
    synonyms: List[str]
    antonyms: List[str]


class AddRelatedWordsRequest(BaseModel):
    words: List[str]


class AddRelatedWordsResponse(BaseModel):
    added: List[str]
    already_had: List[str]
    skipped_no_definition: List[str]


class QuizQuestionResponse(BaseModel):
    word_id: int
    word: str


class QuizAnswerRequest(BaseModel):
    word_id: int
    answer: str


class QuizAnswerResponse(BaseModel):
    verdict: str
    correct: bool
    fsrs_state: str
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    next_review: Optional[str] = None