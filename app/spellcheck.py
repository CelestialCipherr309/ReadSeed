from rapidfuzz import process
def load_dictionary():
    with open("data/words_alpha.txt","r") as file:
        words = file.read().splitlines()
    return words
def suggest_words(word):
    words = [word for word in load_dictionary() if len(word) >= 3]
    matches =process.extract(word,words,limit=1)
    suggested_word,score,index=matches[0]
    if score>=80:
        return suggested_word, score
    else:
        return None,score