from utils import init_database, create_user

if __name__ == "__main__":
    # Initialise Database
    init_database()

    print("User Creation Test")
    username = input("Username: ")
    password = input("Password: ")

    if username and password:
        create_user(username, password)
    else:
        print("Username and password cannot be empty!")
