from fsrs import Scheduler, Card, Rating, State

from storage import get_fsrs_state, update_fsrs_state


scheduler = Scheduler()


def review_word(user_id, word_id, rating):
    saved_state = get_fsrs_state(user_id, word_id)

    if saved_state is None or saved_state["state"] is None:
        card = Card()

    else:
        card = Card(
            state=State(saved_state["state"]),
            step=saved_state["step"],
            stability=saved_state["stability"],
            difficulty=saved_state["difficulty"],
            due=saved_state["due"],
            last_review=saved_state["last_review"]
        )

    card, review_log = scheduler.review_card(
        card,
        rating
    )

    update_fsrs_state(
        user_id=user_id,
        word_id=word_id,
        state=card.state.value,
        step=card.step,
        due=card.due,
        stability=card.stability,
        difficulty=card.difficulty,
        last_review=card.last_review
    )

    return card, review_log