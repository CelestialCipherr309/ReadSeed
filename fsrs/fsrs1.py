from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime, timedelta,timezone
scheduler=Scheduler()
ratings = {
    "Again":Rating.Again,
    "Hard":Rating.Hard,
    "Good":Rating.Good,
    "Easy":Rating.Easy
}
review_time=datetime.now(timezone.utc)
for name,rating in ratings.items():
    card=Card()
    card,review_log=scheduler.review_card(
        card,
        rating,
        review_datetime=review_time
    )
    print(f"\n=== {name} ===")
    print("State:", card.state)
    print("Stability:", card.stability)
    print("Difficulty:", card.difficulty)
    print("Due:", card.due)
