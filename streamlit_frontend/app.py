import html
import os
from collections import OrderedDict
from datetime import datetime

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Override with: READSEED_API_URL=https://your-backend streamlit run app.py
API_URL = os.getenv("READSEED_API_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 15
MAX_HISTORY = 5

# Backend routes. Change these if yours are named differently.
LOOKUP_PATH = "/words/lookup"
CONFIRM_PATH = "/words/confirm"
RELATED_PATH = "/words/related"
RELATED_ADD_PATH = "/words/related/add"
QUIZ_QUESTION_PATH = "/quiz/question"
QUIZ_ANSWER_PATH = "/quiz/answer"  # expects {"word_id": int, "answer": str}
VOCAB_PATH = "/words"  # expects a list of words (or {"words": [...]})

st.set_page_config(page_title="ReadSeed", page_icon="📚", layout="centered")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

    .block-container { max-width: 760px; padding-top: 2.5rem; }

    .headword {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 3rem;
        font-weight: 600;
        line-height: 1.1;
        margin: 0.5rem 0 0.25rem 0;
    }
    .pos { font-style: italic; opacity: 0.7; margin: 1.25rem 0 0.25rem 0; }
    .definition { font-size: 1.05rem; line-height: 1.6; max-width: 65ch; }
    .example { opacity: 0.7; font-style: italic; margin-left: 1.5rem; }
    .your-answer { opacity: 0.75; margin: 0.25rem 0 1rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(value) -> str:
    return html.escape(str(value or ""))


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
def new_quiz_state() -> dict:
    return {
        "phase": "setup",  # setup -> asking -> feedback -> done
        "total": 5,
        "index": 0,
        "score": 0,
        "question": None,
        "feedback": None,
        "results": [],
    }


def init_state() -> None:
    st.session_state.setdefault("lookup_result", None)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("flash", None)
    st.session_state.setdefault("search_word", "")
    st.session_state.setdefault("related_cache", {})
    st.session_state.setdefault("quiz", new_quiz_state())


def queue_lookup(word: str) -> None:
    """Callback: fill the search box and queue a lookup for the Discover page."""
    st.session_state.search_word = word
    st.session_state.pending_lookup = word


def remember(word: str) -> None:
    history = [w for w in st.session_state.history if w.lower() != word.lower()]
    st.session_state.history = [word, *history][:MAX_HISTORY]


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def api_request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    payload: dict | None = None,
) -> tuple[dict | list | None, str | None]:
    """Call the backend. Returns (data, error_message)."""
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            params=params,
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json(), None
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = str(exc.response.json().get("detail", ""))
        except (ValueError, AttributeError):
            pass
        code = exc.response.status_code
        return None, f"The server returned an error ({code}). {detail}".strip()
    except requests.Timeout:
        return None, "The request timed out. Try again in a moment."
    except requests.ConnectionError:
        return None, (
            f"Can't reach ReadSeed's backend at {API_URL}. "
            "Check that FastAPI is running."
        )
    except ValueError:
        return None, "The server sent a response that couldn't be read."
    except requests.RequestException as exc:
        return None, f"Something went wrong: {exc}"


@st.cache_data(ttl=10, show_spinner=False)
def backend_online() -> bool:
    try:
        return requests.get(f"{API_URL}/openapi.json", timeout=2).ok
    except requests.RequestException:
        return False


@st.cache_data(ttl=20, show_spinner=False)
def fetch_vocabulary() -> tuple[dict | list | None, str | None]:
    return api_request("GET", VOCAB_PATH)


def extract_words(payload) -> list[str]:
    """Pull a list of word strings out of a related-words response."""
    if isinstance(payload, dict):
        items = (
            payload.get("related")
            or payload.get("related_words")
            or payload.get("words")
            or []
        )
    else:
        items = payload or []

    words = []
    for item in items:
        if isinstance(item, str):
            words.append(item)
        elif isinstance(item, dict) and item.get("word"):
            words.append(item["word"])
    return words


def humanize_due(iso: str | None) -> str:
    if not iso:
        return "soon"
    try:
        due = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    hours = (due - datetime.now(due.tzinfo)).total_seconds() / 3600
    if hours < 1:
        return "within the hour"
    if hours < 24:
        return f"in about {round(hours)} hours"
    days = round(hours / 24)
    return "tomorrow" if days == 1 else f"in {days} days"


# ---------------------------------------------------------------------------
# Shared rendering
# ---------------------------------------------------------------------------
def render_headword(word: str) -> None:
    st.markdown(f'<div class="headword">{esc(word)}</div>', unsafe_allow_html=True)


def render_meanings(meanings: list[dict]) -> None:
    if not meanings:
        st.info("No definitions came back for this word.")
        return

    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for meaning in meanings:
        pos = meaning.get("part_of_speech") or "other"
        grouped.setdefault(pos, []).append(meaning)

    for pos, items in grouped.items():
        st.markdown(f'<div class="pos">{esc(pos)}</div>', unsafe_allow_html=True)
        for index, item in enumerate(items, start=1):
            st.markdown(
                f'<div class="definition">{index}. {esc(item.get("definition"))}</div>',
                unsafe_allow_html=True,
            )
            if item.get("example"):
                st.markdown(
                    f'<div class="example">“{esc(item["example"])}”</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------
def page_home() -> None:
    st.title("🌱 ReadSeed")
    st.subheader("Grow your vocabulary, one word at a time.")
    st.write(
        "Look up words you don't know, save the ones worth keeping, and "
        "practise them with a quiz that brings each word back right when "
        "you're about to forget it."
    )

    cards = [
        (
            "Discover",
            "Look up a word, read its meanings and find related words.",
            "discover",
        ),
        (
            "Practice",
            "Explain words in your own language. The quiz checks your meaning.",
            "quiz",
        ),
        (
            "My vocabulary",
            "Browse every word you've saved.",
            "vocabulary",
        ),
    ]
    for column, (title, text, key) in zip(st.columns(3), cards):
        with column.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(text)
            if st.button(f"Open {title.lower()}", key=f"home_{key}", use_container_width=True):
                st.switch_page(PAGES[key])


# ---------------------------------------------------------------------------
# Page: Discover
# ---------------------------------------------------------------------------
def save_word(data: dict) -> None:
    with st.spinner("Saving…"):
        result, error = api_request(
            "POST",
            CONFIRM_PATH,
            payload={"word": data["word"], "meanings": data.get("meanings") or []},
        )

    if error:
        st.error(f"Couldn't save the word. {error}")
        return

    message = "Word saved to your vocabulary."
    if isinstance(result, dict):
        message = result.get("message", message)
    st.session_state.flash = (message, "✅")
    st.session_state.lookup_result = {**data, "status": "existing"}
    fetch_vocabulary.clear()
    st.rerun()


def render_related(word: str) -> None:
    st.markdown("### Related words")
    cache = st.session_state.related_cache

    if word not in cache:
        if st.button("Find related words", key=f"find_related_{word}"):
            with st.spinner("Finding related words…"):
                data, error = api_request("GET", RELATED_PATH, params={"word": word})
            if error:
                st.error(error)
            else:
                cache[word] = extract_words(data)
                st.rerun()
        return

    related = cache[word]
    if not related:
        st.caption("No related words found for this one.")
        return

    selected = st.multiselect(
        "Choose words to add to your vocabulary",
        related,
        key=f"related_pick_{word}",
    )
    if st.button("Add selected words", disabled=not selected, key=f"related_add_{word}"):
        with st.spinner("Adding…"):
            result, error = api_request(
                "POST", RELATED_ADD_PATH, payload={"words": selected}
            )
        if error:
            st.error(f"Couldn't add those words. {error}")
        else:
            message = f"Added {len(selected)} word(s) to your vocabulary."
            if isinstance(result, dict):
                message = result.get("message", message)
            st.session_state.flash = (message, "✅")
            fetch_vocabulary.clear()
            st.rerun()


def render_result(data: dict) -> None:
    status = data.get("status")

    if status == "not_found":
        st.warning("We couldn't find that word. Check the spelling and try again.")
        return

    if status == "suggestion":
        suggestion = data.get("suggested_word")
        st.info(f"No exact match. Did you mean **{suggestion}**?")
        if suggestion:
            st.button(
                f"Look up “{suggestion}”",
                on_click=queue_lookup,
                args=(suggestion,),
            )
        return

    render_headword(data.get("word") or "Word")

    if status == "existing":
        st.success("This word is in your vocabulary.")

    render_meanings(data.get("meanings") or [])

    if status == "found":
        st.write("")
        if st.button("Save to my vocabulary", type="primary"):
            save_word(data)

    if data.get("word"):
        st.divider()
        render_related(data["word"])


def render_history() -> None:
    history = st.session_state.history
    if not history:
        return

    st.caption("Recently looked up")
    for column, word in zip(st.columns(len(history)), history):
        column.button(
            word,
            key=f"history_{word.lower()}",
            on_click=queue_lookup,
            args=(word,),
            use_container_width=True,
        )


def page_discover() -> None:
    st.title("Discover")
    st.write("Look up a word to see what it means and find words that go with it.")

    with st.form("word_search_form"):
        st.text_input(
            "Discover a word",
            placeholder="e.g. ephemeral",
            key="search_word",
        )
        st.form_submit_button(
            "Look up word",
            type="primary",
            on_click=lambda: queue_lookup(st.session_state.search_word),
        )

    render_history()

    pending = st.session_state.pop("pending_lookup", None)
    if pending is not None:
        word = pending.strip()
        if not word:
            st.warning("Please enter a word.")
        else:
            with st.spinner(f"Looking up “{word}”…"):
                result, error = api_request("POST", LOOKUP_PATH, payload={"word": word})

            if error:
                st.session_state.lookup_result = None
                st.error(error)
            else:
                st.session_state.lookup_result = result
                if result.get("status") in ("found", "existing"):
                    remember(result.get("word") or word)

    if st.session_state.lookup_result:
        render_result(st.session_state.lookup_result)


# ---------------------------------------------------------------------------
# Page: Quiz
# ---------------------------------------------------------------------------
def verdict_kind(verdict: str | None) -> str:
    if verdict == "EQUIVALENT":
        return "good"
    if verdict and verdict.startswith("PARTIAL"):
        return "partial"
    return "miss"


def load_next_question() -> bool:
    quiz = st.session_state.quiz
    with st.spinner("Picking a word…"):
        data, error = api_request("GET", QUIZ_QUESTION_PATH)
    if error:
        st.error(error)
        return False
    quiz["question"] = data
    quiz["feedback"] = None
    quiz["phase"] = "asking"
    return True


def quiz_setup() -> None:
    quiz = st.session_state.quiz
    st.write(
        "You'll see a word and explain it in your own words. "
        "Close answers count too, and ReadSeed schedules each word "
        "for review based on how well you did."
    )
    total = st.slider("Number of questions", min_value=3, max_value=20, value=5)
    if st.button("Start quiz", type="primary"):
        st.session_state.quiz = {**new_quiz_state(), "total": total}
        if load_next_question():
            st.rerun()


def quiz_asking() -> None:
    quiz = st.session_state.quiz
    question = quiz["question"]

    st.progress(
        quiz["index"] / quiz["total"],
        text=f"Question {quiz['index'] + 1} of {quiz['total']}",
    )
    render_headword(question["word"])

    with st.form(f"quiz_form_{quiz['index']}"):
        answer = st.text_area(
            "What does this word mean?",
            key=f"quiz_answer_{quiz['index']}",
            height=110,
            placeholder="Explain it in your own words",
        )
        submitted = st.form_submit_button("Check answer", type="primary")

    if not submitted:
        return
    if not answer.strip():
        st.warning("Write your answer first.")
        return

    with st.spinner("Checking…"):
        result, error = api_request(
            "POST",
            QUIZ_ANSWER_PATH,
            payload={"word_id": question["word_id"], "answer": answer.strip()},
        )
    if error:
        st.error(f"Couldn't check your answer. {error}")
        return

    feedback = {**result, "answer": answer.strip(), "meanings": []}

    # On a miss, fetch the real meaning so the learner can see it.
    if not result.get("correct"):
        lookup, lookup_error = api_request(
            "POST", LOOKUP_PATH, payload={"word": question["word"]}
        )
        if not lookup_error and isinstance(lookup, dict):
            feedback["meanings"] = lookup.get("meanings") or []

    if result.get("correct"):
        quiz["score"] += 1
    quiz["results"].append(
        {
            "word": question["word"],
            "correct": bool(result.get("correct")),
            "verdict": result.get("verdict"),
        }
    )
    quiz["feedback"] = feedback
    quiz["phase"] = "feedback"
    st.rerun()


def quiz_feedback() -> None:
    quiz = st.session_state.quiz
    question = quiz["question"]
    feedback = quiz["feedback"]

    st.progress(
        (quiz["index"] + 1) / quiz["total"],
        text=f"Question {quiz['index'] + 1} of {quiz['total']}",
    )
    render_headword(question["word"])
    st.markdown(
        f'<div class="your-answer">Your answer: {esc(feedback["answer"])}</div>',
        unsafe_allow_html=True,
    )

    kind = verdict_kind(feedback.get("verdict"))
    if kind == "good":
        st.success("Spot on. That matches the meaning.")
    elif kind == "partial":
        st.warning("Close. Your answer is narrower than the full meaning.")
    else:
        st.error("Not quite.")

    if feedback.get("meanings"):
        st.markdown("### The meaning")
        render_meanings(feedback["meanings"])

    st.info(
        f"You'll see this word again {humanize_due(feedback.get('next_review'))}."
    )
    with st.expander("Memory details"):
        st.write(f"Stage: {feedback.get('fsrs_state', 'unknown')}")
        stability = feedback.get("stability")
        difficulty = feedback.get("difficulty")
        if stability is not None:
            st.write(f"Stability: {stability:.2f} days")
        if difficulty is not None:
            st.write(f"Difficulty: {difficulty:.2f} out of 10")

    is_last = quiz["index"] + 1 >= quiz["total"]
    if is_last:
        if st.button("See results", type="primary"):
            quiz["phase"] = "done"
            st.rerun()
    elif st.button("Next question", type="primary"):
        if load_next_question():
            quiz["index"] += 1
            st.rerun()


def quiz_done() -> None:
    quiz = st.session_state.quiz
    total = quiz["total"]
    score = quiz["score"]

    st.metric("Your score", f"{score} / {total}")
    st.progress(score / total if total else 0)

    st.markdown("### Word by word")
    for item in quiz["results"]:
        icon = "✅" if item["correct"] else "❌"
        label = {
            "good": "Correct",
            "partial": "Close enough",
            "miss": "Needs more practice",
        }[verdict_kind(item["verdict"])]
        st.write(f"{icon} **{item['word']}**: {label}")

    if st.button("Practice again", type="primary"):
        st.session_state.quiz = new_quiz_state()
        st.rerun()


def page_quiz() -> None:
    st.title("Practice")
    phase = st.session_state.quiz["phase"]

    if phase == "setup":
        quiz_setup()
    elif phase == "asking":
        quiz_asking()
    elif phase == "feedback":
        quiz_feedback()
    else:
        quiz_done()

    if phase in ("asking", "feedback"):
        st.write("")
        if st.button("End quiz"):
            st.session_state.quiz = new_quiz_state()
            st.rerun()


# ---------------------------------------------------------------------------
# Page: My vocabulary
# ---------------------------------------------------------------------------
def page_vocabulary() -> None:
    st.title("My vocabulary")

    if st.button("Refresh"):
        fetch_vocabulary.clear()

    data, error = fetch_vocabulary()
    if error:
        st.info(
            "Your vocabulary list isn't available yet. "
            f"The app asks the backend for `GET {VOCAB_PATH}`."
        )
        st.caption(error)
        return

    items = data.get("words", []) if isinstance(data, dict) else (data or [])
    if not items:
        st.info("You haven't saved any words yet. Look one up on the Discover page.")
        return

    query = st.text_input("Filter", placeholder="Search your words").strip().lower()
    shown = 0
    for item in items:
        word = item.get("word", "") if isinstance(item, dict) else str(item)
        if query and query not in word.lower():
            continue
        shown += 1
        with st.expander(word):
            if isinstance(item, dict):
                render_meanings(item.get("meanings") or item.get("definitions") or [])

    st.caption(f"Showing {shown} of {len(items)} words.")


# ---------------------------------------------------------------------------
# App shell
# ---------------------------------------------------------------------------
init_state()

PAGES = {
    "home": st.Page(page_home, title="Home", icon="🌱", default=True),
    "discover": st.Page(page_discover, title="Discover", icon="🔎", url_path="discover"),
    "quiz": st.Page(page_quiz, title="Practice", icon="🧠", url_path="practice"),
    "vocabulary": st.Page(
        page_vocabulary, title="My vocabulary", icon="📚", url_path="vocabulary"
    ),
}

navigation = st.navigation(list(PAGES.values()))

with st.sidebar:
    if backend_online():
        st.caption("🟢 Backend connected")
    else:
        st.caption("🔴 Backend offline")

# One-time messages (e.g. "saved") that must survive st.rerun().
if st.session_state.flash:
    message, icon = st.session_state.flash
    st.toast(message, icon=icon)
    st.session_state.flash = None

navigation.run()