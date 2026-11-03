# 🌱 ReadSeed

**Grow your vocabulary, one word at a time.**

ReadSeed is a full-stack vocabulary app. Look up an unfamiliar word, save the meanings you want to keep, and practise with a quiz that checks what you *mean* instead of matching exact text. A spaced-repetition scheduler (FSRS) decides when each word comes back for review.

The same FastAPI backend powers **two frontends**: a React app and a Streamlit app.

## Demo

[▶ Watch the demo video](https://youtu.be/3uFkgmSff-8?si=DGwO0MgNytVzOb_l)



## Screenshots

| Discover | Practice |
| --- | --- |
| ![Discover page](c:\Users\devya\OneDrive\Pictures\Screenshots\Screenshot 2026-11-02 220721.png , c:\Users\devya\OneDrive\Pictures\Screenshots\Screenshot 2026-11-02 220655.png) | ![Practice page](c:\Users\devya\OneDrive\Pictures\Screenshots\Screenshot 2026-11-02 220740.png) |

| Quiz feedback | My vocabulary |
| --- | --- |
| ![Quiz feedback](c:\Users\devya\OneDrive\Pictures\Screenshots\Screenshot 2026-11-03 154828.png) | ![My vocabulary](c:\Users\devya\OneDrive\Pictures\Screenshots\Screenshot 2026-11-02 220801.png) |

## Features

- **Discover words:** look up a word and read its meanings, grouped by part of speech. Misspellings get a "Did you mean…?" suggestion.
- **Related words:** find words that go with the one you looked up and add several to your vocabulary at once.
- **Personal vocabulary:** save words and browse them later in a searchable list. In the React app, click a word to see its meanings.
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

## How answers are graded

Grading free-text answers is the hardest part of the project. Exact matching fails because there are many correct ways to explain a word, and a single embedding-similarity score fails because opposite meanings (for example "hot" and "cold") can look very similar to an embedding model. ReadSeed combines two models in two stages (`app/semantic_check.py`):

```
Student answer
      │
      ▼
Stage 1: MiniLM (cheap)
  Compare the answer with every stored definition using cosine similarity
  ├─ best score below threshold ──▶ UNRELATED (NLI never runs)
  └─ definitions above threshold
      │
      ▼
Stage 2: NLI cross-encoder (expensive)
  For each remaining definition, test entailment in BOTH directions
      │
      ▼
Verdict: the best result across the checked definitions
```

**Stage 1: MiniLM filter.** The `all-MiniLM-L6-v2` sentence-embedding model turns the answer and each stored definition into vectors and measures cosine similarity. A word can have several definitions, so the answer is compared with all of them, and any definition above the similarity threshold moves on. This is fast, so most wrong answers are rejected here without the heavier model.

**Stage 2: NLI in both directions.** For each remaining definition, the `cross-encoder/nli-deberta-v3-base` model (natural language inference) predicts the probability that one text entails, is neutral to, or contradicts the other. It runs twice:

- **Direction A:** the definition is the premise and the student's answer is the hypothesis.
- **Direction B:** the student's answer is the premise and the definition is the hypothesis.

Checking both directions is what separates a complete answer from a narrower or vaguer one.

| Verdict | How it is decided | Counts as correct | FSRS rating |
| --- | --- | --- | --- |
| **Equivalent** | Both directions entail | Yes | Good |
| **Partial (narrower)** | The answer entails the definition, but not the other way round, so it is more specific | Yes | Hard |
| **Partial (broader)** | The definition entails the answer, but not the other way round, so it is vaguer | No | Again |
| **Contradiction** | Either direction predicts contradiction | No | Again |
| **Unrelated** | None of the above | No | Again |

If a word has several definitions, the best verdict across the checked definitions wins (Equivalent, then Partial narrower, then Partial broader, then Unrelated, then Contradiction).

**Thresholds** (tunable constants at the top of `semantic_check.py`):

| Constant | Value | Role |
| --- | --- | --- |
| `VERY_LOW_THRESHOLD` | 0.30 | If even the best definition scores below this, stop early as unrelated |
| `MINILM_MIN_SIMILARITY` | 0.40 | A definition needs at least this similarity to reach the NLI stage |
| `NLI_ENTAILMENT_THRESHOLD` | 0.70 | Minimum entailment probability to count as entailed |
| `NLI_CONTRADICTION_THRESHOLD` | 0.50 | Minimum contradiction probability to count as a contradiction |

Illustrative example for the word *ephemeral*, whose stored definition is "lasting for a very short time": an answer like "short-lived" should come out as Equivalent, "lasting forever" as a Contradiction, and "a type of fruit" as Unrelated (the exact verdict depends on the model scores).

Each result also includes the similarity score, the NLI probabilities for both directions, the definition that matched best and which stages ran, which makes the grading easy to debug. The experiments behind this design are in [`experiments/`](experiments/).

## Tech stack

| Layer | Tools |
| --- | --- |
| Frontends | React (Vite) and Streamlit |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL |
| Scheduling | FSRS |
| Answer grading | sentence-transformers (MiniLM embeddings), NLI cross-encoder (DeBERTa-v3), PyTorch |
| Data | pandas |

## Architecture

```
React (Vite)  ──┐
                ├──HTTP──▶  FastAPI  ──▶  PostgreSQL
Streamlit     ──┘          (word, quiz,    (words, definitions,
                            review logic)   review state & history)
```

Both frontends talk to the same API, so the app logic lives in one place. The React app calls the backend through `/api`, which Vite's dev server forwards to FastAPI, so no CORS setup is needed during development.

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
├── react_frontend/           # React frontend (Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js        # Dev server and /api proxy
│   └── src/
│       ├── App.jsx           # Discover, Practice and Vocabulary pages
│       ├── api.js            # Backend calls
│       ├── main.jsx
│       └── styles.css
├── streamlit_frontend/
│   └── app.py                # Streamlit frontend
├── data/                     # Word list, definitions and review history
├── ml/                       # Model code (predictor.py)
├── models/                   # Saved models
├── experiments/              # Embedding (MiniLM) and NLI experiments for answer grading
├── notebooks/                # Data exploration
├── fsrs/
├── docs/                     # Screenshots
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer (for the React frontend)
- A running PostgreSQL database

### Setup

```bash
git clone https://github.com/<your-username>/ReadSeed.git
cd ReadSeed

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Configure the database connection used by `app/storage.py` (for example in a `.env` file) before starting the backend.

### Run the backend

```bash
uvicorn app.api_server:app --reload --port 8000
```

The interactive API docs are at http://127.0.0.1:8000/docs.

If you see `No module named 'schemas'`, set `PYTHONPATH` first:

```bash
export PYTHONPATH=app            # PowerShell: $env:PYTHONPATH = "app"
```

### Run the React frontend

In a second terminal:

```bash
cd react_frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Run the Streamlit frontend (optional)

In another terminal, from the project root:

```bash
streamlit run streamlit_frontend/app.py
```

Open http://localhost:8501.

### Pointing a frontend at a different backend

```bash
# Streamlit
READSEED_API_URL=https://your-backend.example.com streamlit run streamlit_frontend/app.py

# React dev server (the proxy target)
READSEED_API_URL=https://your-backend.example.com npm run dev
```

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/words/lookup` | Look up a word (returns `found`, `existing`, `suggestion` or `not_found`) |
| POST | `/words/confirm` | Save a looked-up word and its meanings |
| GET | `/words/related?word=` | Get words related to a given word |
| POST | `/words/related/add` | Add related words to your vocabulary |
| GET | `/words` | List the words in your vocabulary |
| GET | `/quiz/question` | Get a random quiz word |
| POST | `/quiz/answer` | Submit an answer and receive the verdict and next review date |

## Notes and limitations

- The app currently runs as a single user (`CURRENT_USER_ID = 1`), so everyone shares the same progress. Authentication would be the next step for real multi-user use.
- Both grading models are loaded when the backend starts, so startup takes a few seconds and the backend needs enough memory for PyTorch and the models. This matters when choosing where to host it.
- The React app uses Vite's dev proxy to reach the backend. A deployed version needs either a rewrite rule from `/api` to the backend or CORS enabled on FastAPI.

## Roadmap

- [ ] User accounts and login
- [ ] A "due for review" session that uses the FSRS schedule instead of random words
- [ ] Progress charts and review statistics
- [ ] Docker Compose setup for one-command start