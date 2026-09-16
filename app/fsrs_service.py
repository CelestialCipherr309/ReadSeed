from fsrs import Scheduler, Card, Rating, State
from app.storage import get_fsrs_state, update_fsrs_state
scheduler=Scheduler()
def review_word(user_id,word_id,rating):
    #Fetching the current state from our db
    saved_state=get_fsrs_state(user_id,word_id)
    #If no card exists we create a new card
    if saved_state is None:
        card=Card()
    else:
        #reconstructing a card from db
        card=Card(
            state=State(saved_state["state"]),
            step=saved_state["step"], 
            stability=saved_state["stability"], 
            difficulty=saved_state["difficulty"],
            due=saved_state["due"],
            last_review=saved_state["last_review"]
        )
    #give review to fsrs
    card,review_log=scheduler.review_card(card,rating)

    #saving updated state in the db
    update_fsrs_state(user_id=user_id,
        word_id=word_id,
        state=card.state,
        step=card.step,
        due=card.due,
        stability=card.stability,
        difficulty=card.difficulty,
        last_review=card.last_review)
    #returning updated card and review log
    return card, review_log



