from storage import find_word, get_definitions, save_word, add_user_word
from dictionary import get_meaning
from datamuse_api import get_related_words
CURRENT_USER_ID = 1 

def learn_related_words(word):
    existing=find_word(word)
    if existing is not None:
        add_user_word(CURRENT_USER_ID, word["id"])
        print(f"{word} already exists  )")
        return
    meanings= get_meaning(word)
    if meanings is None:
        print(f"  - Skipped '{word}' (no definition found in dictionary).")
        return
    word_id=save_word(word, meanings)

    add_user_word(CURRENT_USER_ID, word_id)
    print(f"  + '{word}' added to your list.")

def offer_related_words(word):
    related= get_related_words(word)
    synonyms= related["synonyms"]  
    antonyms= related["antonyms"]

    if synonyms:
        print(f"\nSynonyms of '{word}':{','.join(synonyms)}")
        ch= input("Do you want to add these words to your list?(y/n)").lower()
        if ch=="y":
            for syn in synonyms:
                learn_related_words(syn)


    if antonyms:
            print(f"\nAntonyms of '{word}':{','.join(antonyms)}")
            ch= input("Do you want to add these words to your list?(y/n)").lower()
            if ch=="y":
                for ant in antonyms:
                    learn_related_words(ant)

    if not synonyms and not antonyms:
        print(f"\n(No synonyms/antonyms found for '{word}'.)")


def add_word_and_show(word, meanings):
    word_id= save_word(word, meanings)
    add_user_word(CURRENT_USER_ID,word_id)

    print(" Word added successfully!")
    print("Meaning:")
    for meaning in meanings:
        print(f"- ({meaning['part_of_speech']}) {meaning['definition']}")

    offer_related_words(word)

    return word_id



