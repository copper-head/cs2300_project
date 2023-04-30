from flask import Flask, request, jsonify
import hashlib
import sqlite3 as sq
import os
import json
import secrets
from datetime import datetime, timedelta

DB_FILE = "database.db"

if not os.path.isfile(DB_FILE):
    print("Database file not found! Run the create_database python script and try again.")
    exit()

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello Comrade!"


@app.route('/api/applicant/login', methods=['POST'])
def applicant_login():

    # Get the username and password from the requets.
    username = request.json['username']
    password = request.json['password']
    
    # Open a sqlite3 connection, verify user login is valid and is
    # an applicant
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    user_query = curs.execute("SELECT password_hash, password_salt, is_enabled, id FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    # Handle Error cases:
    if len(user) != 1:
        err_dict = {"TYPE":"LoginError", "MESSAGE":"Username does not exist."}
        return json.dumps(err_dict)
    elif user[0][-2] != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is disabled."}
        return json.dumps(err_dict)
    
    print(user[0][-1])

    app_query = curs.execute("SELECT user_id FROM applicants WHERE user_id=?", (user[0][-1],))
    app = app_query.fetchall()

    conn.close()

    if len(app) != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is not an applicant."}
        return json.dumps(err_dict)


    feed = (password + user[0][1]).encode('utf-8')
    local_hash = str(hashlib.sha256(feed).hexdigest())

    if local_hash == user[0][0]:
        token = str(secrets.token_hex(32))
        ret_dict = {"TYPE": "LoginSuccess", "MESSAGE":"Login successful.", "TOKEN": token}

        exp_time = datetime.now() + timedelta(hours=3)
        token_exp = exp_time.strftime('%m/%d/%y %H:%M:%S')

        conn = sq.connect(DB_FILE)
        curs = conn.cursor()

        curs.execute("INSERT INTO session_tokens VALUES(?, ?, ?)", (user[0][-1], token, token_exp))

        conn.commit()
        conn.close()

        return json.dumps(ret_dict)
    else:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Invalid password."}
        return json.dumps(err_dict)


@app.route('/api/applicant/create_user', methods=['POST'])
def applicant_create_user():

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
    hash = str(hashlib.sha256(feed).hexdigest())
    
    # Create the user
    curs.execute("INSERT INTO users(user_name, password_hash, password_salt) VALUES (?, ?, ?)", (username, hash, salt))

    # Get the id for the new user
    user_query = curs.execute("SELECT id FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    curs.execute("INSERT INTO applicants(user_id, birth_date, first_name, last_name) VALUES (?,?,?,?)", (user[0][0], birth_date, first_name, last_name))

    conn.commit()
    conn.close()

    return json.dumps({"TYPE":"AccountCreated", "MESSAGE":"Account creation successful."})


# No Authentication Required
@app.route('/api/fetch/welfare_programs', methods=['POST'])
def get_welfare_programs():
    
    username = request.json["username"]
    token = request.json["token"]

    auth_status, message = authenticate(username, token)

    if not auth_status:
        return message
    
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    prog_q = curs.execute("SELECT * FROM welfare_programs")
    progs = prog_q.fetchall()

    payload = {
        "TYPE":"Success",
        "MESSAGE":"Success",
        "payload": str(progs)
    }

    conn.close()

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

def authenticate(user_name, token):

    conn = sq.connect("database.db")
    curs = conn.cursor()

    token_query = curs.execute("SELECT expiration_time FROM session_tokens WHERE token=?",(token,))
    token_dates = token_query.fetchall()

    now = datetime.now()

    if len(token_dates) == 0:
        return (False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Invalid Token."}))
    
    user_query = curs.execute("SELECT id FROM users WHERE user_name=?", (user_name,))
    conn.close()

    token_exp = datetime.strptime(token_dates[0][0], '%m/%d/%y %H:%M:%S')

    if now > token_exp:
        return (False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Session Token Expired."}))
    else:
        return (True, json.dumps({"TYPE":"AuthenticationSuccess", "MESSAGE":"Token Verified."}))

if __name__ == "__main__":
    app.run(debug=True)