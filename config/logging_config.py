import json
import pathlib
import logging.config

"""
Current logging levels, by order of priority:
Critical:   Logged to terminal, file & concern file
Error:      Logged to terminal, file & concern file
Warning:    Logged to terminal & file
Info:       Logged to terminal & file
Debug:      Logged to terminal
"""

def setup_logging():
    config_file = pathlib.Path(__file__).parent / "logging_config.json"
    with open(config_file) as f_in:
        config = json.load(f_in)

    logs_dir = pathlib.Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logging.config.dictConfig(config)
