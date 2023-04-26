from flask import Flask, request, jsonify
import hashlib
import sqlite3 as sq
import os
import json

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

    user_query = curs.execute("SELECT password_hash, password_salt, is_enabled FROM users WHERE user_name='hobobaggi'")
    user = user_query.fetchall()

    print(user)

    conn.close()

    if len(user) != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Username does not exist."}
        return json.dumps(err_dict)
    elif user[-1] != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is disabled."}
        return json.dumps(err_dict)

    local_hash = hashlib.sha256(password + user[1])

    if local_hash == user[0]:
        token = 123
        ret_dict = {"TYPE": "LoginSuccess", "MESSAGE":"Login succesful.", "TOKEN": token}
        return json.dumps(ret_dict)
    else:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Invalid password."}
        return json.dumps(err_dict)


# No Authentication Required
@app.route('/api/fetch/welfare_programs')
def get_welfare_programs():
    pass


# Requires Authentication
@app.rount('/api/post/welfare_app')
def post_welfare_app():
    pass


# Requires Authentication
@app.rount('/api/get/welfare_app')
def post_welfare_app():
    pass

app.route('/api/login', methods=['POST'])
def login():

    username = request.json['username']
    password = request.json['password']

    # Do a sqlite3 query here, return an error if the user does not exist.
    
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    user_query = curs.execute("SELECT password_hash, password_salt, is_enabled FROM users WHERE user_name='hobobaggi'")
    user = user_query.fetchall()

    print(user)

    conn.close()

    if len(user) != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Username does not exist."}
        return json.dumps(err_dict)
    elif user[-1] != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is disabled."}
        return json.dumps(err_dict)

    local_hash = hashlib.sha256(password + user[1])

    if local_hash == user[0]:
        token = 123
        ret_dict = {"TYPE": "LoginSuccess", "MESSAGE":"Login succesful.", "TOKEN": token}
        return json.dumps(ret_dict)
    else:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Invalid password."}
        return json.dumps(err_dict)

### ==================== REVIEW STAFF ROUTES ==================== ###

# Login

if __name__ == "__main__":
    app.run(debug=True)