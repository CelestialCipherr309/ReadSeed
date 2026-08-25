from learn import learn_related_words,offer_related_words,add_word_and_show
from storage import find_word, get_definitions, save_word, add_user_word, load_words
from dictionary import get_meaning
from spellcheck import suggest_words
from quiz import start_quiz
CURRENT_USER_ID = 1
while True:

    print("\n Welcome to ReadSeed!")
    print("1. Learn a new word")
    print("2. View all words")
    print("3. Take a quiz")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        word = input("Enter a word: ")

        existing_word = find_word(word)

        if existing_word is not None:
            print(" You have already learned this word!")

            word_id = existing_word["id"]

            meanings = get_definitions(word_id)

            print("Meaning:")

            for meaning in meanings:
                print(
                    f"- ({meaning['part_of_speech']}) "
                    f"{meaning['definition']}"
                )

        else:
            meanings = get_meaning(word)

            if meanings is None:
                suggested_word, score = suggest_words(word)

                if suggested_word is None:
                    print(" Word not found.")

                else:
                    print(f"Did you mean '{suggested_word}'?")

                    confirmation = input("Enter y/n: ").lower()

                    if confirmation == "y":
                        meanings = get_meaning(suggested_word)

                        if meanings is not None:
                            add_word_and_show(suggested_word, meanings)
                        else:
                            print("Could not find the suggested")
                    else:
                        print('Okay word not added')
            else:
                add_word_and_show(word, meanings)

                
    elif choice == "2":

        print(load_words())

    elif choice == "3":

        num_questions = int(input("How many questions? "))
        start_quiz(num_questions)

    elif choice == "4":

        print("\n Goodbye!")
        break

    else:

        print("\n Invalid choice. Please try again.")