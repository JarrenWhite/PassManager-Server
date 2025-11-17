from json import load as load_json
from pathlib import Path
from typing import Optional, Dict, Any
import logging.config

"""
Current logging levels, by order of priority:
Critical:   Logged to terminal, file & concern file
Error:      Logged to terminal, file & concern file
Warning:    Logged to terminal & file
Info:       Logged to terminal & file
Debug:      Logged to terminal
"""

"""
Logging messages are to start with capitalisations,
and use full grammar, including ending punctuation.
"""

def setup_logging(log_dir: Path, config_path: Optional[Path] = None):
    if not config_path:
        config_path = Path(__file__).parent / "logging_config.json"

    with config_path.open("r") as f_in:
        config: Dict[str, Any] = load_json(f_in)

    log_dir.mkdir(parents=True, exist_ok=True)

    handlers = config.get("handlers", {})
    for handler in handlers.values():
        if "filename" in handler:
            original = Path(handler["filename"]).name
            handler["filename"] = str(log_dir / original)

    logging.config.dictConfig(config)
