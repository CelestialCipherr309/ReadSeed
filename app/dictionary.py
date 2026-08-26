import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")

def get_meaning(word):
    url = f"https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if not data or isinstance(data[0],str):
            return None
        

        meanings = []

        for entry in data:
            part_of_speech = entry.get("fl","unknown")
            for definition in entry.get("shortdef",[]):
                meanings.append({
                    "part_of_speech": part_of_speech,
                    "definition": definition
                })

        return meanings

    else:
        return None