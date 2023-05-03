import requests
import json

API_BASE_URL = "http://localhost:5000"

head = {"Content-Type":"application/json"}

user_token = None
username = None
first_name = None
last_name = None

def welcome():

    print("Welcome Citizen!\n")

    user_input = ""
    while user_input != "y" and user_input != "n":
        user_input =  input("Do you have an exisitng account? (y/n): ")
            
    if user_input == "n":
        create_account()
    else:
        login()
    
    # Once we're logged in we need to have a menu or something.

    return user_input

def login():

    input_valid = False

    while not input_valid:

        print()
        username = input("username: ")
        password = input("password: ")

        url = API_BASE_URL + '/api/applicant/login'
        payload = json.dumps({"username":username,"password":password})
        response = requests.request("POST", url, headers=head, data=payload)

        response_info = json.loads(response.text)

        if response_info["TYPE"] == "LoginError":
            print(response_info["MESSAGE"])
        elif response_info["TYPE"] == "LoginSuccess":
            print("Login Successful!")
            user_token = response_info["TOKEN"]
            input_valid = True
    
def create_account():

    input_valid = False

    while not input_valid:

        ### ***************** ADD LOGIC TO MAKE IT TO WHERE THESE CANNOT BE BLANK AND ARE VALID ETC **************** ###
        username = input("username: ")
        password = input("password: ")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        birth_date = input("Date of Birth: ")

        url = API_BASE_URL + '/api/applicant/create_user'
        payload = json.dumps(
            {
                "username":username,
                "password":password,
                "firstname":first_name,
                "lastname":last_name,
                "birthdate":birth_date
            }
        )

        response = requests.request("POST", url, headers=head, data=payload)

        response_info = json.loads(response.text)

        if response_info["TYPE"] == "AccountCreationError":
            print(response_info["MESSAGE"])
        elif response_info["TYPE"] == "AccountCreated":
            print("Account Creation Successful! Use your new credentials to log in:\n")
            input_valid = True
    login()


def main_menu():
    pass

def view_welfare_programs():
    pass

def view_submitted_applications():
    pass

def submit_new_application():
    pass

if __name__ == '__main__':
    welcome()
    
    



