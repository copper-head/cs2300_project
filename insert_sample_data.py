from os.path import isfile
import sqlite3 as sq
DB_NAME = "database.db"

if isfile(DB_NAME) and isfile("sample_data.sql"):    
    conn = sq.connect(DB_NAME)    
    curs = conn.cursor()       
    with open("sample_data.sql", "r") as file:        
        schema_text = file.read()        
        curs.executescript(schema_text)
    
    conn.commit()
    conn.close()