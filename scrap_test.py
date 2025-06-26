from database import init_db, get_session_local, User

def create_user(username, password):
    """Create a new user with the given username and password"""
    session = get_session_local()()
    
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create new user
        password_hash = password
        new_user = User(username=username, password_hash=password_hash)
        
        session.add(new_user)
        session.commit()
        
        print(f"User '{username}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating user: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    init_db()

    print("User Creation Test")
    username = input("Username: ")
    password = input("Password: ")

    if username and password:
        create_user(username, password)
    else:
        print("Username and password cannot be empty!")
