import json
import pathlib
import logging.config

def setup_logging():
    config_file = pathlib.Path(__file__).parent / "logging_config.json"
    with open(config_file) as f_in:
        config = json.load(f_in)
    
    logs_dir = pathlib.Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logging.config.dictConfig(config)
