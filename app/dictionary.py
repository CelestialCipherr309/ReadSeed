import requests


def get_meaning(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        meanings = []

        for meaning in data[0]["meanings"]:
            part_of_speech = meaning["partOfSpeech"]

            for definition in meaning["definitions"]:
                meanings.append({
                    "part_of_speech": part_of_speech,
                    "definition": definition["definition"]
                })

        return meanings

    else:
        return None