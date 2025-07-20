from utils import Database
from config import setup_logging

if __name__ == "__main__":
    # Set up logging config
    setup_logging()

    # Initialise Database
    Database.init_database()

    print("User Creation Test")
    username = input("Username: ")
    password = input("Password: ")

    if username and password:
        Database.create_user(username, password)
    else:
        print("Username and password cannot be empty!")
