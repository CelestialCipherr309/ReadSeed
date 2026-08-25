# Algorithms

## Algorithm 1: Learn a New Word

### Purpose
Allow the user to enter a word, check whether it already exists in the database, fetch its meaning if necessary, and associate the word with the current user.

### Steps

1. Ask the user to enter a word.

2. Search the `words` table to check whether the word already exists.

3. If the word already exists:
   - Retrieve its `word_id`.
   - Retrieve its definitions from the `definitions` table.
   - Display the stored definitions.
   - Do not create a duplicate word or definition.

4. If the word does not exist:
   - Request the word's meanings from the Dictionary API.

5. If the API finds the word:
   - Save the word in the `words` table.
   - Save all of its definitions in the `definitions` table.
   - Retrieve the newly generated `word_id`.
   - Create a relationship between the current user and the word in the `user_words` table.
   - Display the fetched definitions.

6. If the API cannot find the word:
   - Use the word-suggestion algorithm to find a possible match.

7. If a suggestion is found:
   - Ask the user whether they want to use the suggested word.
   - If the user accepts:
     - Fetch the suggested word's meanings.
     - Save the word and its definitions.
     - Retrieve its `word_id`.
     - Associate the word with the current user through `user_words`.
     - Display the definitions.
   - If the user rejects the suggestion:
     - Do not add anything to the database.

8. If no suggestion is found:
   - Inform the user that the word could not be found.

### Data Flow

User Input
→ Check `words`
→ Existing Word?
→ Yes: Get stored definitions
→ No: Dictionary API
→ Save word + definitions
→ Get `word_id`
→ Create `user_words` relationship