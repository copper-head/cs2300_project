import requests
import json

API_BASE_URL = "http://localhost:5000"

head = {"Content-Type":"application/json"}

user_token = None
g_user_name = None
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
            global user_token
            global g_user_name
            g_user_name = username
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

    url = API_BASE_URL + "/api/get/welfare_programs"
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
    print('Press Enter to exit to the menu\n')

    url = API_BASE_URL + "/api/applicant/view_applications"
    payload = json.dumps({"username": g_user_name,"token": user_token})
    response = requests.request("POST", url, headers=head, data=payload)
    applications = json.loads(response.text)
    
    print("{:<30}".format("Date and Time Submitted")+"{:<30}".format("Welfare Submitted To")+"Review Status")
    print("{:-<73}".format('-'))
    for i in applications["data"]:
        for j  in i:
                print('{:<30}'.format(j), end='')
        print()

    input()
    main_menu()
    

def submit_new_application():
    appName = ''
    valid = False
    while not valid:
        appName = input("Choose a valid welfare program to apply for ('q' to quit): ")
        if(appName == 'q'):
            valid = True
            break
        #Check for Validity application name
        #Load all welfare plans, check the name for each one
        url = API_BASE_URL + "/api/get/welfare_programs"
        response = requests.request("GET", url, headers=head)
        welfares = json.loads(response.text)
        for i in welfares["payload"]:
            if appName == i[0]:
                #begin prompting for more info
                print("\nYou have chosen to apply to the "+appName+" welfare program")
                print("Please fill out the following prompts. Remember to press enter when you fill the field.")
                income = input('Please state your income from all sources last year: ')
                disabledStatus = int(input('Please type 1 if you have a disability, 0 otherwise: '))
                score = int(input('Please state how many Reliability Points you have: '))
                print('Thank you for submitting an application. Exiting to the menu...')
        

                url = API_BASE_URL + "/api/applicant/submit_application"
                payload = json.dumps({
                    "username": g_user_name,
                    "token": user_token,
                    "welfare_program": appName,
                    "last_year_income": income,
                    "has_disability": disabledStatus,
                    "reliability_points": score
                    })
                headers = head
                response = requests.request("POST", url, headers=head, data=payload) 
                valid = True
    main_menu()

if __name__ == '__main__':
    welcome()
    
    



