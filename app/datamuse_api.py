import requests

DATAMUSE_BASE_URL="https://api.datamuse.com/words"

def get_synonyms(word, max_results=10):
    """Fetches the synonyms using the rel_syn relation 
    in datamuse
    if no related synonyms found , it returns an empty list
    
    """
    params={"rel_syn":word,"max":max_results}
    response= requests.get(DATAMUSE_BASE_URL,params=params)
    if response.status_code!=200:
        return []
    results=response.json()

    return [item["word"] for item in results]

def get_antonyms(word, max_results=10):
    """Fetches the antonyms using the rel_ant relation 
        in datamuse
        if no related antonyms found , it returns an empty list
        
        """
    params={"rel_ant":word,"max":max_results}
    response= requests.get(DATAMUSE_BASE_URL,params=params)
    if response.status_code!=200:
        return []
    results= response.json()
    return [item["word"] for item in results]

def get_related_words(word,max_results=10):
    """convenience func; gets both synonyms and antonyms for 
    a word
    in one call
    """
    return {"synonyms":get_synonyms(word,max_results=max_results),
            "antonyms":get_antonyms(word,max_results=max_results)
            }

if __name__ == "__main__":
    # Quick manual check
    test_word = "happy"
    related = get_related_words(test_word)
    print(f"Word: {test_word}")
    print("Synonyms:", related["synonyms"])
    print("Antonyms:", related["antonyms"])

