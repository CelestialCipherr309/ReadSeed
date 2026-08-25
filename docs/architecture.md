# ReadSeed Architecture

## 1. Project Overview

ReadSeed is a vocabulary-learning application that helps users learn
new words, store their definitions, and review those words over time.

The application uses Python for application logic and PostgreSQL
for persistent data storage.

---

## 2. Project Structure

```text
ReadSeed/
│
├── app/
│   ├── main.py
│   ├── storage.py
│   ├── quiz.py
│   └── ...
│
├── data/
│   └── ...
│
├── docs/
│   ├── architecture.md
│   └── algorithms.md
│
└── sql/
    └── schema.sql
3. Application Architecture

ReadSeed is divided into several logical layers.

Application Entry Point

main.py

Responsible for:

Displaying the main menu.
Taking user input.
Calling the appropriate functions.
Controlling the overall application flow.
Application Logic

Files such as quiz.py contain the logic for individual features.

Examples:

Selecting words for quizzes.
Running quizzes.
Evaluating answers.
Calculating quiz scores.
Handling learning-related operations.
Data Access Layer

storage.py

Responsible for communicating with PostgreSQL.

It handles operations such as:

Connecting to the database.
Finding words.
Saving words.
Saving definitions.
Retrieving definitions.
Managing user-word relationships.
Recording review information.

The application logic should use functions from storage.py
instead of writing SQL queries directly inside main.py or quiz.py.

External API

The Dictionary API is used when a word is not already stored
in the database.

The general flow is:

User
 ↓
Application
 ↓
Dictionary API
 ↓
Application
 ↓
PostgreSQL
4. Database Architecture

PostgreSQL is used as the persistent database for ReadSeed.

Main Tables
users

Stores information about users.

words

Stores unique vocabulary words.

definitions

Stores one or more definitions for each word.

content_sources

Stores information about sources from which words may originate.

word_contexts

Stores contextual information about words, such as example sentences
or their position within a source.

user_words

Connects users with the words they are learning.

review_events

Stores the history of a user's reviews of words.

5. Database Relationships
users
  │
  ├────────────── user_words ────────────── words
  │                                           │
  │                                           │
  │                                      definitions
  │
  └────────────── review_events ─────────── words

content_sources
        │
        └────────────── word_contexts ────── words
User → Words

A user can learn many words.

A word can be learned by many users.

Therefore, user_words acts as the relationship between
users and words.

Word → Definitions

A word can have multiple definitions.

Therefore, definitions references words using word_id.

Word → Context

A word can appear in different contexts or sources.

Therefore, word_contexts stores contextual information
associated with a word.

User → Review Events

A user can review the same word many times.

Each review is stored as a separate record in review_events.

6. Learn Word Architecture

When a user chooses the "Learn a new word" option,
the application follows this general flow:

User enters word
        ↓
main.py
        ↓
Check words table
        ↓
   ┌────┴────┐
   │         │
Exists    Does not exist
   │         │
   ↓         ↓
Get       Dictionary API
stored       ↓
definitions  Get meanings
   │         ↓
   │       Save word
   │       + definitions
   │         ↓
   └────→ word_id
             ↓
        user_words
             ↓
           User

If the word already exists, its stored definitions are retrieved
instead of calling the Dictionary API again.

If the word does not exist, the Dictionary API is used to retrieve
its meanings. The word and its definitions are then stored in
PostgreSQL.

7. Quiz Architecture

The quiz system uses words stored in the database.

General flow:

User
 ↓
main.py
 ↓
quiz.py
 ↓
Select a word
 ↓
Ask the user for its meaning
 ↓
Evaluate the answer
 ↓
Record review information
 ↓
review_events

The quiz system is separate from the basic word-storage system.

8. Spaced Repetition Architecture

Spaced repetition will use the user's review history.

The application will store individual review attempts in
review_events.

The spaced-repetition algorithm will later analyze this history
to determine when a word should be reviewed again.

The exact spaced-repetition algorithm has not yet been finalized.

Therefore, scheduling logic is kept separate from the basic
word-storage system.

9. Design Principles
Separation of Responsibilities

Each part of the application has a specific responsibility.

main.py
    ↓
Application flow

quiz.py
    ↓
Quiz logic

storage.py
    ↓
Database operations

PostgreSQL
    ↓
Persistent data
Avoid Duplicate Data

Words are stored once in the words table.

Definitions are stored separately and linked through word_id.

Users are connected to words through user_words.

Keep Review History

Review attempts are stored as individual events in
review_events rather than overwriting previous attempts.

This allows the spaced-repetition system to analyze a user's
learning history later.

10. Future Extensions

The architecture is designed to support future features such as:

User authentication.
Personalized learning.
Spaced repetition.
Review scheduling.
Word difficulty tracking.
Reading-context tracking.
Multiple content sources.
More advanced quiz types.
Learning analytics.