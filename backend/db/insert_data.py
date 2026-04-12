from pathlib import Path
from faker import Faker
import random
from tqdm import tqdm
import os
from SurgeonConstants import *
from db_connections import CURSOR, CONN


def insert_fake_data():
    """Fills the db with fake data"""
    print("Creating the db schema")



    # creates the scheme
    file = open(Path("./SurgeonDatabaseSchema.sql"), "r")
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
    CONN.commit()

    CURSOR.execute("SELECT specialty_id FROM specialties")
    specialty_ids = [row[0] for row in CURSOR.fetchall()]
    CURSOR.execute("SELECT campus_id FROM campuses")
    campus_ids = [row[0] for row in CURSOR.fetchall()]
    CURSOR.execute("SELECT operation_id FROM operations")
    operation_ids = [row[0] for row in CURSOR.fetchall()]
   # CURSOR.execute("SELECT surgeon_id FROM surgeon_demographics")
    #surgeon_ids =  [row[0] for row in CURSOR.fetchall()]

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

        

        # get the id for the next two foriegn keys
        
        surgeon_id: int = CURSOR.lastrowid

         # each surgeon does multiple operations
        chosen_ops = random.sample(operation_ids, k=random.randint(1, 5))

        for op_id in chosen_ops:
            count = random.randint(1, 100)

            CURSOR.execute("""
            INSERT INTO operation_counts (operation_id, surgeon_id, count)
            VALUES (?, ?, ?)
        """, (op_id, surgeon_id, count))
        

        #print(f"Full Name: {full_name}, Degree: {degree}, Gender: {gender}, Address: {address}, Languages: {languages}, Specialties: {specialties}")

    CONN.commit()
    CURSOR.close()
    print("Finished imputing data into the database!")

if __name__ == "__main__":
     insert_fake_data()