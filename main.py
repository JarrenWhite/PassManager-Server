from pathlib import Path

from utils import setup_logging, DatabaseConfig
from database import DatabaseSetup, Base


def initialise_config():
    DatabaseConfig.load()


def initialise_logging():
    logging_path = DatabaseConfig.get_path("logging")

    if not logging_path:
        logging_path = Path("./logs")

    log_config_path = DatabaseConfig.get_path("log_config")
    setup_logging(logging_path, log_config_path)


def initialise_database():
    database_path = DatabaseConfig.get_path("database")

    if not database_path:
        database_path = Path("./data")

    DatabaseSetup.init_db(database_path, Base)


def main():
    initialise_config()
    initialise_logging()
    initialise_database()


if __name__ == "__main__":
    main()
