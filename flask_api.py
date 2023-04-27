from flask import Flask, request, jsonify
import hashlib
import sqlite3 as sq
import os
import json
import secrets
from datetime import datetime

DB_FILE = "database.db"

if not os.path.isfile(DB_FILE):
    print("Database file not found! Run the create_database python script and try again.")
    exit()

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello Comrade!"

@app.route('/api/login', methods=['POST'])
def login():

    username = request.json['username']
    password = request.json['password']

    # Do a sqlite3 query here, return an error if the user does not exist.
    
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    user_query = curs.execute("SELECT password_hash, password_salt, is_enabled FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    conn.close()

    if len(user) != 1:
        err_dict = {"TYPE":"LoginError", "MESSAGE":"Username does not exist."}
        return json.dumps(err_dict)
    elif user[-1] != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is disabled."}
        return json.dumps(err_dict)

    local_hash = hashlib.sha256(password + user[1])

    if local_hash == user[0]:
        token = str(secrets.hex(32))
        ret_dict = {"TYPE": "LoginSuccess", "MESSAGE":"Login succesful.", "TOKEN": token}

        conn = sq.connect(DB_FILE)
        curs = conn.cursor()

        user_query = curs.execute("SELECT password_hash, password_salt, is_enabled FROM applicants WHERE user_name=?", (username,))
        user = user_query.fetchall()

        conn.close()

        return json.dumps(ret_dict)
    else:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Invalid password."}
        return json.dumps(err_dict)


@app.route('/api/create_app_user', methods=['POST'])
def create_user():

    # Fetch parameters from json file and put them into variables
    username = request.json["username"]
    password = request.json["password"]
    first_name = request.json["firstname"]
    last_name = request.json["lastname"]
    birth_date = request.json["birthdate"]


    conn = sq.connect(DB_FILE)                  # Open a connection to the DB
    curs = conn.cursor()                        # Create a cursor for the connection

    # Look to see if the user alread exists
    user_query = curs.execute("SELECT * FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    # If the user already exists, respond with an error
    if len(user) != 0:
        err_dict = {"TYPE":"AccountCreationError", "MESSAGE":"Username already exists."}
        return json.dumps(err_dict)
    
    # Create a salt and a hash for the new user
    salt = secrets.token_hex(16)
    feed = (password + salt).encode('utf-8')
    hash_obj = hashlib.sha256(feed)
    hash = str(hash.hexdigest())
    
    # Create the user
    curs.execute("INSERT INTO users VALUES (?, ?, ?, 1)", (username, hash, salt))

    # Get the id for the new user
    user_query = curs.execute("SELECT id FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    curs.execute("INSERT INTO applicants VALUES (?,?,?,?)", (user[0], birth_date, first_name, last_name))

    conn.close()

    return json.dumps({"TYPE":"AccountCreated", "MESSAGE":"Account creation successful."})




# No Authentication Required
@app.route('/api/fetch/welfare_programs', methods=['POST'])
def get_welfare_programs():
    
    user_id = request.json["user_id"]
    token = request.json["token"]

    conn = sqlite3.connect(DB_FILE)
    curs = conn.cursor()

    curs.execute("SELECT expiration_time FROM session_tokens WHERE user_id=? and token=?", (user_id, token))
    sessions = curs.fetchall()

    now = datetime.now()

    valid_token = False
    for i in sessions:

        token_exp = datetime.strptime(i[0], '%m/%d/%y %H:%M:%S')

        if token_exp > datetime.now():
            valid_token = True

    if not valid_token:
        conn.close()
        return json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"No valid token available. Sign in required."})
    else:

        prog_q = curs.execute("SELECT * FROM welfare_programs")
        progs = prog_q.fetchall()

        payload = 
        {
            "TYPE":"Success",
            "MESSAGE":"Success",
            "payload": progs
        }

        return json.dumps(payload)




# Requires Authentication
@app.route('/api/post/welfare_app')
def post_welfare_app():
    pass


# Requires Authentication
@app.route('/api/get/welfare_app')
def get_welfare_app():
    pass

### ==================== REVIEW STAFF ROUTES ==================== ###

# Login

def authenticate(user_id, token):

    conn = sq.connect("database.db")
    curs = conn.cursor()

    token_query = curs.execute("SELECT expiration_time FROM session_tokens WHERE user_id=?",(user_id,))
    token_dates = token_query.fetchall()

    now = datetime.now()

    for time in token_dates:

        t_time = datetime.strptime(i[0], '%m/%d/%y %H:%M:%S')

if __name__ == "__main__":
    app.run(debug=True)