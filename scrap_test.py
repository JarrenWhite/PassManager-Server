from utils import create_user

if __name__ == "__main__":
    print("User Creation Test")
    username = input("Username: ")
    password = input("Password: ")

    if username and password:
        create_user(username, password)
    else:
        print("Username and password cannot be empty!")
