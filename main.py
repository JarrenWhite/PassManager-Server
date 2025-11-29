import sys
from pathlib import Path

from logging import getLogger
logger = getLogger("database")

from utils import setup_logging, DatabaseConfig
from database import DatabaseSetup, Base


def initialise_config(config_path = None):
    DatabaseConfig.load(config_path)


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
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    else:
        config_path = None

    try:
        initialise_config(config_path)
        initialise_logging()
        initialise_database()
    except Exception:
        logger.exception("Failed during application initialisation")
        sys.exit(1)


if __name__ == "__main__":
    main()
