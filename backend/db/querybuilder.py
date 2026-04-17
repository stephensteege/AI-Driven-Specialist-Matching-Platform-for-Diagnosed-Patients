from db_connections import CURSOR, CONN
def BuildDatabaseQuery(slots):
   
    
    joins = []
    conditions = []
    parameters = []
    
    #Begin Query
    query = """
    SELECT
        s.first_name,
        s.last_name,
        SUM(oc.count) AS total_operations,
        s.office_phone
    FROM surgeon_demographics s
    JOIN operation_counts oc ON s.surgeon_id = oc.surgeon_id
    """

    #Operation Filter
    if slots.get("operation"):
        joins.append("JOIN operations o ON oc.operation_id = o.operation_id")

        operation_conditions = []
        for term in slots['operation']:
            operation_conditions.append("o.operation_name LIKE ?")
            parameters.append(f"%{term}%")
        conditions.append("(" + " OR ".join(operation_conditions) + ")")
    
    #Specialty Filter
    if slots.get("specialty"):
        joins.append("JOIN specialties sp ON s.specialty_id = sp.specialty_id")

        specialty_conditions = []
        for term in slots['specialty']:
            specialty_conditions.append("sp.specialty_name LIKE ?")
            parameters.append(f"%{term}%")
        conditions.append("(" + " OR ".join(specialty_conditions) + ")")

    #Campus Filter
    if slots.get("location"):
        joins.append("JOIN campuses c ON s.campus_id = c.campus_id")

        campus_conditions = []
        for term in slots['location']:
            campus_conditions.append("c.campus_name LIKE ?")
            parameters.append(f"%{term}%")
        conditions.append("(" + " OR ".join(campus_conditions) + ")")

    #Language Filter
    if slots.get("language"):
        joins.append("JOIN surgeon_languages sl ON s.surgeon_id = sl.surgeon_id")
        joins.append("JOIN languages l ON sl.language_id = l.language_id")

        language_conditions = []
        for term in slots['language']:
            language_conditions.append("l.language_name LIKE ?")
            parameters.append(f"%{term}%")
        conditions.append("(" + " OR ".join(language_conditions) + ")")

    #Add the JOINS
    query += "\n".join(set(joins))

    #Add our Where statements
    if conditions:
        query += "\nWHERE " + " AND ".join(conditions)

    #Finish the Query
    query += """
    GROUP BY s.surgeon_id
    ORDER BY total_operations DESC
    LIMIT 3
    """ 
    print(query)
    return query,parameters



slots = {
    "operation": [],
    "specialty": [],
    "location": [],
    "language": []
}


query, params = BuildDatabaseQuery(slots)

CURSOR.execute(query, params)
results = CURSOR.fetchall()

for row in results:
    print(row)

