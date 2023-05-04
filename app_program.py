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
            print("\nLogin Successful!")
            user_token = response_info["TOKEN"]
            input_valid = True
            main_menu()
    
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
    
    input_valid = False
    exit = False
    while not input_valid:

        print("\nSelect an action: ")
        print("1 - View Welfare Programs")
        print("2 - View Submitted Applications")
        print("3 - Submit New Application")
        print("4 - Exit")

        user_input = input()
        print()

        if user_input == "1":
            input_valid = True
            view_welfare_programs()
        elif user_input == "2":
            input_valid = True
            view_submitted_applications()
        elif user_input == "3":
            input_valid = True
            submit_new_application()
        elif user_input == "4":
            input_valid = True
            print("GOODBYE!")
            exit()
        else:
            print("Invalid Input")




            

def view_welfare_programs():
    print('Press Enter to exit to the menu\n')

    url = "http://localhost:5000/api/get/welfare_programs"
    response = requests.request("GET", url, headers=head)
   
    welfares = json.loads(response.text)
    print('{:<20}'.format('Name')+'{:<20}'.format('Type') + 'Available Tiers')
    print('{:-<55}'.format('-'))
    for i in welfares["payload"]:
        for j  in i:
                print('{:<20}'.format(j), end='')
        print()

    input()
    main_menu()


def view_submitted_applications():
    #very similar to view_welfare_program
    #just use the right url and format to include the app no.
    pass

def submit_new_application():
    appName = ''
    valid = False
    while not valid:
        appName = input("Choose a welfare program to apply for ('q' to quit): ")
        #FIXME: check if appName is valid
        #if valid, give confirmation message and exit
        if(appName == 'q'):
            valid = True
    main_menu()

if __name__ == '__main__':
    welcome()
    
    



