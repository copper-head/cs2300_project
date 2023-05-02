import request
import json

API_BASE_URL = "http://localhost:5000"

head = {"Content-Type":"application/json"}

user_token = None
usr_input = welcome()


def welcome():

    print("Welcome Citizen!\n")

    input_valid = False

    while not input_valid:
        user_input =  input("Do you have an exisitng account? (y/n):")

    return user_input

def create_account():

    input_valid = False

    while not input_valid:

        username = input("username: ")
        password = input("password: ")

        url = API_BASE_URL + '/api/applicant/login'
        payload = json.dumps({"username":username,"password":password})
        response = requests.request("POST", url, headers=head, data=payload)

        response_info = json.loads(response.text)
        print(response_info)

        input_valid = True




    
    
    



