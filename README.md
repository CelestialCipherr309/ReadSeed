# 🌱 ReadSeed

**Grow your vocabulary, one word at a time.**

ReadSeed is a full-stack vocabulary app. Look up an unfamiliar word, save the meanings you want to keep, and practise with a quiz that checks what you *mean* instead of matching exact text. A spaced-repetition scheduler (FSRS) decides when each word comes back for review.




## Features

- **Discover words:** look up a word and read its meanings, grouped by part of speech. Misspellings get a "Did you mean…?" suggestion.
- **Related words:** find words that go with the one you looked up and add several to your vocabulary at once.
- **Personal vocabulary:** save words and browse them later in a searchable list.
- **Meaning-based quiz:** explain a word in your own words. Answers are graded by semantic similarity, so a correct paraphrase counts and exact wording isn't required.
- **Spaced repetition:** each answer updates the word's review schedule with the FSRS algorithm, and the quiz tells you when you'll see the word again.

## How the quiz works

1. The backend picks a random word from your vocabulary.
2. Your answer is compared with the word's stored definitions by a semantic check.
3. The verdict is converted into an FSRS rating:

| Semantic verdict | Counts as correct | FSRS rating |
| --- | --- | --- |
| Equivalent | Yes | Good |
| Partial (your answer is narrower) | Yes | Hard |
| Anything else | No | Again |

4. FSRS updates the word's state, stability, difficulty and next due date, which are stored in PostgreSQL along with the attempt history.

## Tech stack

| Layer | Tools |
| --- | --- |
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL |
| Scheduling | FSRS |
| Data | pandas |

## Architecture

```
Streamlit  ──HTTP──▶  FastAPI  ──▶  PostgreSQL
 (UI)                (word, quiz,     (words, definitions,
                      review logic)    review state & history)
```

## Project structure



```
ReadSeed/
├── app/                      # FastAPI backend
│   ├── main.py
│   ├── api_server.py         # API routes
│   ├── learn_api.py
│   ├── quiz_api.py
│   ├── schemas.py            # Request/response models
│   ├── datamuse_api.py       # Related-words lookup
│   ├── dictionary.py
│   ├── spellcheck.py         # "Did you mean…?" suggestions
│   ├── storage.py            # Database access
│   ├── quiz.py               # Quiz logic
│   ├── semantic_check.py     # Answer grading
│   ├── fsrs_service.py       # FSRS scheduling
│   ├── sm2.py                # SM-2 scheduling
│   └── learn.py
├── data/                     # Word list, definitions and review history
├── ml/                       # Model code (predictor.py)
├── models/                   # Saved models
├── experiments/              # Embedding (MiniLM) and NLI experiments for answer grading
├── notebooks/                # Data exploration
├── fsrs/
├── docs/                     # Screenshots
├── streamlit_frontend/
│   └── app.py                # Streamlit frontend
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- A running PostgreSQL database


### Run

Start the backend and the frontend in two separate terminals:

```bash
# Terminal 1: FastAPI backend
uvicorn app.api_server:app --reload --port 8000

# Terminal 2: Streamlit frontend
streamlit run streamlit_app.py
```

Open http://localhost:8501. The interactive API docs are at http://127.0.0.1:8000/docs.

To point the frontend at a different backend, set `READSEED_API_URL`:

```bash
READSEED_API_URL=https://your-backend.example.com streamlit run streamlit_app.py
```

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/words/lookup` | Look up a word (returns `found`, `existing`, `suggestion` or `not_found`) |
| POST | `/words/confirm` | Save a looked-up word and its meanings |
| GET | `/words/related?word=` | Get words related to a given word |
| POST | `/words/related/add` | Add related words to your vocabulary |
| GET | `/quiz/question` | Get a random quiz word |
| POST | `/quiz/answer` | Submit an answer and receive the verdict and next review date |

## Notes and limitations

- The app currently runs as a single user (`CURRENT_USER_ID = 1`), so everyone shares the same progress. Authentication would be the next step for real multi-user use.
- Free hosting tiers put idle services to sleep, which causes the slow first load mentioned above.

## Roadmap

- [ ] User accounts and login
- [ ] A "due for review" session that uses the FSRS schedule instead of random words
- [ ] Progress charts and review statistics



