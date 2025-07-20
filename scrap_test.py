from utils import Database
from config import setup_logging
from flask import Flask
from api import user_bp

# While in test mode, the apis are only visile to the local PC
test_mode = True

def initialise_application():
    setup_logging()
    Database.init_database()

def run_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)

    if test_mode:
        print("Starting application in Test mode...")
        print("APIs will be accessible at: http://127.0.0.1:5000")
        print("You can test this using curl and calling the APIs.")
        print("For more information, see the README.")
        app.run(debug=True, host='127.0.0.1', port=5000)

    else:
        print("Starting application in Production mode...")
        print("APIs will be accessible at: http://0.0.0.0:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    initialise_application()
    run_app()
