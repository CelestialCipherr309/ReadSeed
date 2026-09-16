import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from fsrs import Rating

from app.fsrs_service import review_word


user_id = 1
word_id = 1

card, review_log = review_word(
    user_id,
    word_id,
    Rating.Good
)

print("\nUpdated FSRS Card:")
print("State:", card.state)
print("Step:", card.step)
print("Stability:", card.stability)
print("Difficulty:", card.difficulty)
print("Due:", card.due)
print("Last Review:", card.last_review)