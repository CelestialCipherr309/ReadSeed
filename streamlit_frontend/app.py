import requests
import streamlit as st

# FastAPI backend address
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="ReadSeed",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 ReadSeed")
st.subheader("Grow your vocabulary, one word at a time.")

st.write(
    "Discover unfamiliar words, understand their meanings, "
    "and build vocabulary that lasts."
)

# Store the latest lookup between Streamlit reruns.
if "lookup_result" not in st.session_state:
    st.session_state.lookup_result = None

# Word search form
with st.form("word_search_form"):
    if "suggested_word" in st.session_state:
        st.session_state.search_word = st.session_state.pop("suggested_word")
    word = st.text_input(
    "Discover a word",
    placeholder="e.g. ephemeral",
    key="search_word",
)

    search_clicked = st.form_submit_button(
        "Look up word",
        type="primary",
    )

# Send the lookup request to FastAPI.
if search_clicked:
    if not word.strip():
        st.warning("Please enter a word.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/words/lookup",
                json={"word": word.strip()},
                timeout=15,
            )
            response.raise_for_status()

            st.session_state.lookup_result = response.json()

        except requests.RequestException as exc:
            st.error(
                "Could not connect to ReadSeed's backend. "
                "Check that FastAPI is running on port 8000."
            )
            st.caption(f"Technical details: {exc}")

# Display the lookup result.
data = st.session_state.lookup_result

if data:
    status = data.get("status")

    if status == "not_found":
        st.warning("Word not found. Check the spelling.")

    elif status == "suggestion":
        suggestion = data.get("suggested_word")
        st.info(f"Did you mean: {suggestion}?")

        if suggestion and st.button("Look up suggested word"):
            st.session_state.lookup_result = None
            st.session_state.suggested_word = suggestion
            st.rerun()

    else:
        st.header(data.get("word") or "Word")

        if status == "existing":
            st.success("This word is already in your vocabulary.")

        meanings = data.get("meanings") or []

        if meanings:
            st.markdown("### Meanings")

            for meaning in meanings:
                st.markdown(
                    f"**{meaning['part_of_speech']}**"
                )
                st.write(meaning["definition"])

        if status == "found":
            if st.button("Save to my vocabulary"):
                try:
                    saved = requests.post(
                        f"{API_URL}/words/confirm",
                        json={
                            "word": data["word"],
                            "meanings": meanings,
                        },
                        timeout=15,
                    )
                    saved.raise_for_status()

                    st.success(
                        saved.json().get(
                            "message",
                            "Word saved successfully.",
                        )
                    )

                    # Avoid offering to save the same result again.
                    st.session_state.lookup_result = {
                        **data,
                        "status": "existing",
                    }
                    st.rerun()

                except requests.RequestException as exc:
                    st.error(f"Could not save the word: {exc}")
