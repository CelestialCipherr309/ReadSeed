import os
from collections import OrderedDict

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Override with: READSEED_API_URL=https://your-backend streamlit run app.py
API_URL = os.getenv("READSEED_API_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 15
MAX_HISTORY = 5

st.set_page_config(
    page_title="ReadSeed",
    page_icon="📚",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

    .block-container { max-width: 720px; padding-top: 2.5rem; }

    .headword {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 3rem;
        font-weight: 600;
        line-height: 1.1;
        margin: 0.5rem 0 0.25rem 0;
    }
    .pos {
        font-style: italic;
        opacity: 0.7;
        margin: 1.25rem 0 0.25rem 0;
    }
    .definition { font-size: 1.05rem; line-height: 1.6; max-width: 65ch; }
    .example { opacity: 0.7; font-style: italic; margin-left: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
def init_state() -> None:
    st.session_state.setdefault("lookup_result", None)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("flash", None)
    st.session_state.setdefault("search_word", "")


def queue_lookup(word: str) -> None:
    """Callback: set the input box and ask the main flow to run a lookup.

    Callbacks run before the widgets are drawn, so it is safe to change the
    text input's value here (this replaces the old `suggested_word` trick).
    """
    st.session_state.search_word = word
    st.session_state.pending_lookup = word


def remember(word: str) -> None:
    history = [w for w in st.session_state.history if w.lower() != word.lower()]
    st.session_state.history = [word, *history][:MAX_HISTORY]


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def api_post(path: str, payload: dict) -> tuple[dict | None, str | None]:
    """POST to the backend. Returns (data, error_message)."""
    try:
        response = requests.post(
            f"{API_URL}{path}", json=payload, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json(), None
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except ValueError:
            pass
        status_code = exc.response.status_code
        return None, f"The server returned an error ({status_code}). {detail}".strip()
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


def save_word(data: dict) -> None:
    with st.spinner("Saving…"):
        result, error = api_post(
            "/words/confirm",
            {"word": data["word"], "meanings": data.get("meanings") or []},
        )

    if error:
        st.error(f"Couldn't save the word. {error}")
        return

    st.session_state.flash = (
        result.get("message", "Word saved to your vocabulary."),
        "✅",
    )
    # Avoid offering to save the same result again.
    st.session_state.lookup_result = {**data, "status": "existing"}
    st.rerun()


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render_meanings(meanings: list[dict]) -> None:
    if not meanings:
        st.info("No definitions came back for this word.")
        return

    # Group definitions under their part of speech, keeping original order.
    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for meaning in meanings:
        pos = meaning.get("part_of_speech") or "other"
        grouped.setdefault(pos, []).append(meaning)

    for pos, items in grouped.items():
        st.markdown(f'<div class="pos">{pos}</div>', unsafe_allow_html=True)
        for index, item in enumerate(items, start=1):
            definition = item.get("definition", "")
            st.markdown(
                f'<div class="definition">{index}. {definition}</div>',
                unsafe_allow_html=True,
            )
            if item.get("example"):
                st.markdown(
                    f'<div class="example">“{item["example"]}”</div>',
                    unsafe_allow_html=True,
                )


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

    # status is "found" (new word) or "existing" (already saved)
    st.markdown(
        f'<div class="headword">{data.get("word") or "Word"}</div>',
        unsafe_allow_html=True,
    )

    if status == "existing":
        st.success("This word is in your vocabulary.")

    render_meanings(data.get("meanings") or [])

    if status == "found":
        st.write("")
        if st.button("Save to my vocabulary", type="primary"):
            save_word(data)


def render_history() -> None:
    history = st.session_state.history
    if not history:
        return

    st.caption("Recently looked up")
    columns = st.columns(len(history))
    for column, word in zip(columns, history):
        column.button(
            word,
            key=f"history_{word.lower()}",
            on_click=queue_lookup,
            args=(word,),
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
init_state()

st.title("🌱 ReadSeed")
st.subheader("Grow your vocabulary, one word at a time.")
st.write(
    "Discover unfamiliar words, understand their meanings, "
    "and build vocabulary that lasts."
)

# Show one-time messages (e.g. "saved") that must survive st.rerun().
if st.session_state.flash:
    message, icon = st.session_state.flash
    st.toast(message, icon=icon)
    st.session_state.flash = None

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

# Run a lookup if one was queued by the form, a suggestion, or a history chip.
pending = st.session_state.pop("pending_lookup", None)
if pending is not None:
    word = pending.strip()
    if not word:
        st.warning("Please enter a word.")
    else:
        with st.spinner(f"Looking up “{word}”…"):
            result, error = api_post("/words/lookup", {"word": word})

        if error:
            st.session_state.lookup_result = None
            st.error(error)
        else:
            st.session_state.lookup_result = result
            if result.get("status") in ("found", "existing"):
                remember(result.get("word") or word)

if st.session_state.lookup_result:
    render_result(st.session_state.lookup_result)