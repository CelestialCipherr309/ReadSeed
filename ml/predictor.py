from data.dictionary import dictionary
def get_meaning(word):
    meaning = dictionary.get(word.lower())
    if meaning:
        return meaning
    else:
        return "Meaning not found in the dictionary."
word = input("Enter a word:")   
print(get_meaning(word)) 