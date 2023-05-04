import requests
import json

API_BASE_URL = "http://localhost:5000"
head = {"Content-Type":"application/json"}

g_user_name = None
staff_token = None

def staff_login():
    
    print("Please input your staff login credentials\n")
    username = input("username: ")
    password = input("password: ")

    url = API_BASE_URL + "/api/staff/login"

    payload = json.dumps({"username":username,"password":password})
    response = requests.request("POST", url, headers=head, data=payload)

    response_info = json.loads(response.text)

    if response_info["TYPE"] == "LoginError":
        print(response_info["MESSAGE"])
    elif response_info["TYPE"] == "LoginSuccess":
        print("Login Successful!")
        global staff_token
        global g_user_name
        g_user_name = username
        staff_token = response_info["TOKEN"]
        reviewMenu()

def reviewMenu():

    print()
    exit_program = False
    while not exit_program:

        print("select an action: ")
        print("1 - Review application")
        print("2 - View unreviewed application list")
        print("3 - Exit")

        staff_input = input()
        print()

        if staff_input == "1":
            reviewApplication()
        elif staff_input == "2":
            print("Implement Me")
        elif staff_input == "3":
            print("GOODBYE!")
            exit()
        else:
            print("Invalid Input")

def reviewApplication():
    #grab application for review. Accept/Deny/Do nothing
    url = "http://localhost:5000/api/staff/view_application"

    payload = json.dumps({
    "username": "BIG_BOY",
    "token": "34a9571c72be8646537b04b30f2c6ce83fcf6eb88d66c1dcc137afd066b88984"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    #response is in JSON

    print("submission Date: " + response["Data"][2])
    print("Welfare Program: " + response["Data"][3])
    print("Yearly Income: " + response["Data"][4])
    if response["Data"][5] == 0:
        print("Has Disability: No")
    else:
        print("Has Disability: Yes")
    print("Reliability Points: " + response["Data"][6])
    print()

    decision = False
    accepted = ""
    while decision == False:
        print("Choose an action:")
        print("1 - Accept Application")
        print("2 - Deny Application")
        print("3 - Put Application back in to be reviewed")

        staff_input = input()
        print()

        if staff_input == "1":
            decision = True
            accepted = True
        elif staff_input == "2":
            decision = True
            accepted = False
        elif staff_input == "3":
            decision = True
            accepted = False #Not functional yet
        else:
            print("Invalid Input")

    url = "http://localhost:5000/api/staff/submit_app_review"

    payload = json.dumps({
    "username": "BIG_BOY",
    "token": staff_token,
    "application_id": response["Data"][2],
    "is_accepted": accepted
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print("Application Review Submitted")


if __name__ == '__main__':

    staff_login()