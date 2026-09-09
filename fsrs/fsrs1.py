from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime, timedelta,timezone
scheduler=Scheduler()
card=Card()
print("New card:")
print("State:", card.state)
print("Due:", card.due)
print("Stability:", card.stability)
print("Difficulty:", card.difficulty)

time1= datetime.now(timezone.utc)
card,log=scheduler.review_card(
    card,
    Rating.Good,
    review_datetime=time1
)

print("\n=== REVIEW 1: GOOD ===")
print("State:", card.state)
print("Due:", card.due)
print("Stability:", card.stability)
print("Difficulty:", card.difficulty)

time2=time1+timedelta(days=1)

card,log=scheduler.review_card(
    card,
    Rating.Good,
    review_datetime=time2
)
print("\n=== REVIEW 2: GOOD (1 DAY LATER) ===")
print("State:", card.state)
print("Due:", card.due)
print("Stability:", card.stability)
print("Difficulty:", card.difficulty)


time3=time1+timedelta(days=3)
card,log=scheduler.review_card(
    card,
    Rating.Good,
    review_datetime=time3
)
print("\n=== REVIEW 3: GOOD (3 DAYS LATER) ===")
print("State:", card.state)
print("Due:", card.due)
print("Stability:", card.stability)
print("Difficulty:", card.difficulty)
