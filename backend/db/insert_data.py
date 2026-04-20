from pathlib import Path
from faker import Faker
import random
from tqdm import tqdm
import os
from db.db_connections import CURSOR, CONN
from db.SurgeonConstants import *

def insert_fake_data():
    """Fills the db with fake data"""
    print("Creating the db schema")

    # creates the scheme
    schema_path = Path(__file__).resolve().parent / "SurgeonDatabaseSchema.sql"
    file = open(schema_path, "r")
    create_tables = file.read()
    file.close()
        
    CURSOR.executescript(create_tables)
    CONN.commit()

    fake = Faker()

    CURSOR.execute("BEGIN") # start a transaction to speed up inserts

    for specialty in FAKE_SPECIALTIES:
        CURSOR.execute(
            "INSERT INTO specialties (specialty_name) VALUES (?)",
            (specialty,)
        )

    for campus  in FAKE_CAMPUS:
        CURSOR.execute(
            "INSERT INTO campuses (campus_name) VALUES (?)",
            (campus,)
        )

    for operations in FAKE_OPERATIONS:
        CURSOR.execute(
            "INSERT INTO operations (operation_name) VALUES (?)",
            (operations,)
        )

    for language in FAKE_LANGUAGES:
        CURSOR.execute(
        "INSERT INTO languages (language_name) VALUES (?)",
        (language,)
    )
    CONN.commit()

    CURSOR.execute("SELECT specialty_id FROM specialties")
    specialty_ids = [row[0] for row in CURSOR.fetchall()]
    CURSOR.execute("SELECT campus_id FROM campuses")
    campus_ids = [row[0] for row in CURSOR.fetchall()]
    CURSOR.execute("SELECT operation_id FROM operations")
    operation_ids = [row[0] for row in CURSOR.fetchall()]
    CURSOR.execute("SELECT language_id FROM languages")
    language_ids = [row[0] for row in CURSOR.fetchall()]

    CURSOR.execute("SELECT language_id FROM languages WHERE language_name = ?", ("English",))
    english_id = CURSOR.fetchone()[0]

    for index in tqdm(range(AMOUNT_OF_PHYSICIANS)):

        # gethering fake data for our surgeon demographic
        first_name: str = fake.first_name()
        last_name: str = fake.last_name()
        gender: str = random.choice(FAKE_GENDER)
        specialty_id  = random.choice(specialty_ids)
        campus_id: str = random.choice(campus_ids)
        office_phone =  "(" + str(random.randint(100,999)) + ")" + str(random.randint(1000000,9999999))
        
        #inserting the previous data into our surgeon demopgraphic table
        CURSOR.execute("""
            INSERT INTO surgeon_demographics (first_name, last_name, gender, specialty_id, campus_id, office_phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, gender, specialty_id, campus_id, office_phone))

        surgeon_id: int = CURSOR.lastrowid

        #INSEERT ENGLISH AS A DEFAULT VALUE TO ALL SURGEONS
        CURSOR.execute("""
            INSERT INTO surgeon_languages (surgeon_id, language_id)
            VALUES (?, ?)
            """, (surgeon_id, english_id))
        
        # remove English from the language pool
        other_language_ids = [lid for lid in language_ids if lid != english_id]

        # assign 0–2 additional languages
        chosen_languages = []
        if other_language_ids:
            chosen_languages = random.sample(
                other_language_ids,
                k=random.randint(0, min(2, len(other_language_ids)))
            )

        for lang_id in chosen_languages:
            CURSOR.execute("""
                INSERT INTO surgeon_languages (surgeon_id, language_id)
                VALUES (?, ?)
            """, (surgeon_id, lang_id))
        # get the id for the next two foriegn keys
        
         # each surgeon does multiple operations
        chosen_ops = random.sample(operation_ids, k=random.randint(1, 5))

        for op_id in chosen_ops:
            count = random.randint(1, 100)

            CURSOR.execute("""
            INSERT INTO operation_counts (operation_id, surgeon_id, count)
            VALUES (?, ?, ?)
        """, (op_id, surgeon_id, count))
            
        #print(f"Full Name: {full_name}, Degree: {degree}, Gender: {gender}, Address: {address}, Languages: {languages}, Specialties: {specialties}")

        #Test Case Doctors
        #Surgeon ID 2001: John Smith General Surgery Speaks English, Spanish, preforms hernia repair
    CURSOR.execute("""
    INSERT INTO surgeon_demographics(first_name, last_name, gender, specialty_id, campus_id, office_phone)
                   VALUES(?, ?, ?, ?, ?, ?)
                   """, ("John", "Smith", "M", 63, 2, "(111)1111111"))

    test_surgeon_id = CURSOR.lastrowid

    CURSOR.execute("""
    INSERT INTO operation_counts(operation_id, surgeon_id, count)
                   VALUES (?, ?, ?)
                    """, (2, test_surgeon_id, 500))

    CURSOR.execute(""" 
    INSERT INTO surgeon_languages(surgeon_id, language_id)
                   VALUES(?, ?)
    """, (test_surgeon_id, 6))

    CURSOR.execute(""" 
    INSERT INTO surgeon_languages(surgeon_id, language_id)
                   VALUES(?, ?)
    """, (test_surgeon_id, 24))
    
    CONN.commit()
    CURSOR.close()
    print("Finished imputing data into the database!")

if __name__ == "__main__":
     insert_fake_data()