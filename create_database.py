from os.path import isfile
import sqlite3 as sq
DB_NAME = "database.db"

if not isfile(DB_NAME) and isfile("schema.sql"):    
    conn = sq.connect(DB_NAME)    
    curs = conn.cursor()       
    with open("schema.sql", "r") as file:        
        schema_text = file.read()        
        curs.executescript(schema_text)