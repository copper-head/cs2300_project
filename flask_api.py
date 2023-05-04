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


# Requires Authentication
@app.route('/api/applicant/submit_application', methods=['POST'])
def post_welfare_app():

    username = request.json["username"]
    token = request.json["token"]
    
    # Authenticate and throw an error if token is invalid.
    auth, message = authenticate(username, token)
    if not auth:
        return message

    conn = sq.connect("database.db")
    curs = conn.cursor()

    curs.execute("SELECT applicants.id FROM users JOIN applicants ON users.id = applicants.user_id WHERE users.user_name=?", (username,))
    app_id = curs.fetchone()[0]

    values = (
        app_id,
        datetime.now().strftime('%m/%d/%y %H:%M:%S'),
        request.json["welfare_program"],
        request.json["last_year_income"],
        request.json["has_disability"],
        request.json["reliability_points"]
    )

    curs.execute("INSERT INTO applications(applicant_id, submission_date, ly_income, welfare_program, has_disability, reliability_points) VALUES(?,?,?,?,?,?)", values)
    conn.commit()
    conn.close()

    return json.dumps({"TYPE":"ApplicationSumbitted", "MESSAGE":"Application Was Submitted Successfully"})



# Requires Authentication
@app.route('/api/applicant/view_applications', methods=['POST'])
def get_welfare_app():
    
    username = request.json["username"]
    token = request.json["token"]
    
    # Authenticate and throw an error if token is invalid.
    auth, message = authenticate(username, token)
    if not auth:
        return message


    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    curs.execute("SELECT applications.submission_date, applications.welfare_program, applications.review_status FROM (SELECT applicants.id FROM users JOIN applicants ON users.id = applicants.user_id WHERE users.user_name=?) AS applier JOIN applications ON applications.applicant_id = applier.id", (username,) )
    results = curs.fetchall()

    conn.close()

    return json.dumps({"TYPE":"QuerySuccess", "MESSAGE":"Query Ran Successfully.", "data":results})
    
    


### ==================== REVIEW STAFF ROUTES ==================== ###

# Login

@app.route('/api/staff/login', methods=['POST'])
def staff_login():
    
    # Get the username and password from the requets.
    username = request.json['username']
    password = request.json['password']
    
    # Open a sqlite3 connection, verify user login is valid and is a staff member
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    user_query = curs.execute("SELECT password_hash, password_salt, is_enabled, id FROM users WHERE user_name=?", (username,))
    user = user_query.fetchall()

    # Handle Error cases:
    if len(user) != 1:
        err_dict = {"TYPE":"LoginError", "MESSAGE":"Username does not exist."}
        return json.dumps(err_dict)
    elif user[0][-2] != 1:
        err_dict = {"TYPE":"LoginError", "MESSAGE":"User is disabled."}
        return json.dumps(err_dict)

    app_query = curs.execute("SELECT user_id FROM review_staff WHERE user_id=?", (user[0][-1],))
    app = app_query.fetchall()

    conn.close()

    if len(app) != 1:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"User is not authorized."}
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

        curs.execute("INSERT INTO staff_tokens VALUES(?, ?, ?)", (user[0][-1], token, token_exp))

        conn.commit()
        conn.close()

        return json.dumps(ret_dict)
    else:
        err_dict = {"TYPE": "LoginError", "MESSAGE":"Invalid password."}
        return json.dumps(err_dict)


@app.route("/api/staff/view_application", methods=['POST'])
def staff_view_application():

    username = request.json["username"]
    token = request.json["token"]
    
    # Authenticate and throw an error if token is invalid.
    auth, message = staff_authenticate(username, token)
    if not auth:
        return message

    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    curs.execute("SELECT * FROM applications WHERE review_status='unreviewed' LIMIT 1")
    app_data = curs.fetchall()

    if len(app_data) == 0:
        return json.dumps({"TYPE":"ApplicationViewWarning","MESSAGE":"No applications to review."})

    curs.execute("UPDATE applications SET review_status='in_review' WHERE id=?", (app_data[0][0],))
    conn.commit()
    conn.close()

    return json.dumps({"TYPE":"ApplicationViewSuccess","MESSAGE":"Application Pulled Successfully.","data":app_data[0]})

@app.route("/api/staff/view_unreviewed_applications", methods=['POST'])
def staff_view_all_applications():

    username = request.json["username"]
    token = request.json["token"]
    
    # Authenticate and throw an error if token is invalid.
    auth, message = staff_authenticate(username, token)
    if not auth:
        return message

    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    curs.execute("SELECT * FROM applications WHERE review_status='unreviewed'")
    app_data = curs.fetchall()

    if len(app_data) == 0:
        return json.dumps({"TYPE":"ApplicationViewWarning","MESSAGE":"No applications to review."})

    conn.close()

    return json.dumps({"TYPE":"ApplicationViewSuccess","MESSAGE":"Applications Pulled Successfully.","data":app_data[0]})


@app.route('/api/staff/submit_app_review', methods=['POST'])
def submit_app_review():
    
    username = request.json["username"]
    token = request.json["token"]
    application_id = request.json["application_id"]
    is_accepted = request.json["is_accepted"]

    # Authenticate and throw an error if token is invalid.
    auth, message = staff_authenticate(username, token)
    if not auth:
        return message

    conn = sq.connect(DB_FILE)
    curs = conn.cursor()

    curs.execute("SELECT * FROM applications WHERE id = ? AND review_status != 'accepted' AND review_status != 'rejected'", (application_id,))
    app_data = curs.fetchall()

    if len(app_data) == 0:
        return json.dumps({"TYPE":"ReviewSubmissionError","MESSAGE":"Id does not correspond to an open application."})

    if is_accepted:
        curs.execute("UPDATE applications SET review_status='accepted' WHERE id=?", (application_id,))
    else:
        curs.execute("UPDATE applications SET review_status='rejected' WHERE id=?", (application_id,))

    conn.commit()
    conn.close()

    return json.dumps({"TYPE":"ReviewSubmissionSuccess","MESSAGE":"Review submission successfully submitted."})


### ==================== NO AUTHENTICAITON REQUIRED ==================== ###

@app.route('/api/get/welfare_programs')
def get_welfare_programs():
    
    ### FETCH DATA ###
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()
    prog_q = curs.execute("SELECT name, plan_type FROM welfare_programs")
    progs = prog_q.fetchall()
    conn.close()

    # Encapsulate data and send.
    payload = {
        "type":"Success",
        "message":"Success",
        "payload": progs
    }

    return json.dumps(payload)

@app.route('/api/get/welfare_program_names')
def get_program_names():
    
    ### FETCH DATA ###
    conn = sq.connect(DB_FILE)
    curs = conn.cursor()
    prog_q = curs.execute("SELECT name FROM welfare_programs")
    progs = prog_q.fetchall()
    conn.close()

    # Encapsulate data and send.
    payload = {
        "type":"Success",
        "message":"Success",
        "payload": str(progs)
    }

    return json.dumps(payload)


### ================ DEMONSTRATION CALLS ================ ###
#
# These calls are purely for testing purposes and would not be included in a production environment!
#
#

@app.route('/debug/create/staff_user', methods=['POST'])
def create_staff_user():

    # Fetch parameters from json file and put them into variables
    username = request.json["username"]
    password = request.json["password"]
    first_name = request.json["firstname"]
    last_name = request.json["lastname"]


    conn = sq.connect(DB_FILE)                  # Open a connection to the DB
    curs = conn.cursor()                        # Create a cursor for the connection

    # Look to see if the user already exists
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

    curs.execute("INSERT INTO review_staff(user_id, first_name, last_name) VALUES (?,?,?)", (user[0][0], first_name, last_name))

    conn.commit()
    conn.close()

    return json.dumps({"TYPE":"AccountCreated", "MESSAGE":"Account creation successful."})



def authenticate(user_name, token):

    conn = sq.connect("database.db")
    curs = conn.cursor()

    token_query = curs.execute("SELECT expiration_time FROM session_tokens WHERE token=? and user_id = (SELECT id FROM users WHERE user_name = ?)",(token, user_name))
    token_dates = token_query.fetchall()

    now = datetime.now()

    if len(token_dates) == 0:
        return False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Invalid Token."})
    
    conn.close()

    token_exp = datetime.strptime(token_dates[0][0], '%m/%d/%y %H:%M:%S')

    if now > token_exp:
        return False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Session Token Expired."})
    else:
        return True, json.dumps({"TYPE":"AuthenticationSuccess", "MESSAGE":"Token Verified."})
    

def staff_authenticate(user_name, token):

    conn = sq.connect("database.db")
    curs = conn.cursor()

    token_query = curs.execute("SELECT expiration_time FROM staff_tokens WHERE token=? and user_id = (SELECT id FROM users WHERE user_name = ?)",(token, user_name))
    token_dates = token_query.fetchall()

    now = datetime.now()

    if len(token_dates) == 0:
        return False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Invalid Token."})
    
    conn.close()

    token_exp = datetime.strptime(token_dates[0][0], '%m/%d/%y %H:%M:%S')

    if now > token_exp:
        return False, json.dumps({"TYPE":"AuthenticationError", "MESSAGE":"Session Token Expired."})
    else:
        return True, json.dumps({"TYPE":"AuthenticationSuccess", "MESSAGE":"Token Verified."})


if __name__ == "__main__":
    app.run(debug=True)