import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("POSTGRES_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="readseed",
        user="postgres",
        password=password,
        port="5432"
    )


def load_words():
    conn = get_connection()

    query = """
        SELECT *
        FROM words;
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df
def save_word(word, meanings):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO words (word)
        VALUES (%s)
        RETURNING id;
        """,
        (word,)
    )

    word_id = cursor.fetchone()[0]

    for meaning in meanings:
        cursor.execute(
            """
            INSERT INTO definitions
            (word_id, part_of_speech, definition)
            VALUES (%s, %s, %s);
            """,
            (
                word_id,
                meaning["part_of_speech"],
                meaning["definition"]
            )
        )

    conn.commit()

    cursor.close()
    conn.close()

    return word_id
def find_word(word):
   conn = get_connection()
   cursor=conn.cursor()

   cursor.execute(
       """
      SELECT id,word
      FROM words
      WHERE LOWER(word)=LOWER(%s);
        
       """,
       (word,)
   )
   result= cursor.fetchone()


   cursor.close()
   conn.close()

   if result is None:
       return None
   
   return {
        "id":result[0],
        "word":result[1]

    }
def get_definitions(word_id):
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute(
        """
        SELECT part_of_speech, definition
        FROM definitions
        WHERE word_id= %s;
           
          """,
          (word_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    definitions=[]
    for row in results:
        definitions.append({
            "part_of_speech":row[0],
            "definition":row[1]
        })
    return definitions
def add_user_word(user_id,word_id, word_context_id):
    conn= get_connection()
    cursor=conn.cursor()

    cursor.execute(
        """
         INSERT INTO user_words
         (user_id,word_id, word_context_id)
         VALUES(%s,%s,%s)
         """,
         (user_id,word_id, word_context_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
def save_review_event(user_id, word_id, was_correct, response_time_ms, review_type):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO review_events
        (user_id, word_id, was_correct, response_time_ms, review_type)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (
            user_id,
            word_id,
            was_correct,
            response_time_ms,
            review_type
        )
    )

    conn.commit()

    cursor.close()
    conn.close()
def add_user_word(user_id, word_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM user_words
        WHERE user_id = %s AND word_id = %s;
        """,
        (user_id, word_id)
    )

    existing = cursor.fetchone()

    if existing is not None:
        cursor.close()
        conn.close()
        return existing[0]

    cursor.execute(
        """
        INSERT INTO user_words (user_id, word_id)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (user_id, word_id)
    )

    user_word_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return user_word_id
def add_review_event(user_id, word_id,was_correct, review_type):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute(
        """
        INSERT INTO review_events(
        user_id,
        word_id,
        was_correct,
        review_type
        )
        VALUES(%s,%s,%s,%s)
        RETURNING id;
        
        """,
        (user_id, word_id,was_correct, review_type)

    )
    review_event_id =cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return review_event_id
def get_user_word_state(user_id,word_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        """
        SELECT repetitions, interval_days,ease_factor
        FROM user_words
        WHERE user_id=%s AND word_id=%s
        """,
        (user_id,word_id)
    )
    result=cursor.fetchone()
    cursor.close()
    conn.close()
    if result is None:
        return None
    return {
        "repetitions":result[0],
        "previous_interval":result[1],
        "ease_factor":float(result[2])

    }
