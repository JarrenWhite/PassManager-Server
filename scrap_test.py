from utils import DatabaseUtils

if __name__ == "__main__":
    # Initialise Database
    DatabaseUtils.init_database()

    print("User Creation Test")
    username = input("Username: ")
    password = input("Password: ")

    if username and password:
        DatabaseUtils.create_user(username, password)
    else:
        print("Username and password cannot be empty!")
