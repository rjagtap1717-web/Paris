import logging
import json
import traceback
from datetime import datetime
from pathlib import Path
import sys

_BASE_DIR = Path(__file__).resolve().parent.parent
_LOG_DIR = _BASE_DIR / "logs"
_LOG_FILE = _LOG_DIR / "paris_debug.log"

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "time": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(log_obj)

class OutputRedirector:
    def __init__(self, logger, level, original_stream):
        self.logger = logger
        self.level = level
        self.original_stream = original_stream

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            if line:
                self.logger.log(self.level, line)
        self.original_stream.write(buf)
        self.original_stream.flush()

    def flush(self):
        self.original_stream.flush()

def setup_logging():
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("PARIS")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # File handler for structured JSON logging
    file_handler = logging.FileHandler(_LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Redirect stdout and stderr
    sys.stdout = OutputRedirector(logger, logging.INFO, sys.stdout)
    sys.stderr = OutputRedirector(logger, logging.ERROR, sys.stderr)
    
    return logger

def get_logger(name):
    return logging.getLogger(name)
