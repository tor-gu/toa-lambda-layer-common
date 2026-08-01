import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum


class Domain(str, Enum):
    SCORING_PIPELINE = "scoring_pipeline"
    SCORE_API = "score_api"


_STANDARD_LOG_RECORD_FIELDS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "taskName",
    }
)


class _JsonFormatter(logging.Formatter):
    def __init__(self, *, module: str, domain: Domain):
        super().__init__()
        self._module = module
        self._domain = domain

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        log_obj = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "app": "toa",
            "domain": self._domain,
            "module": self._module,
            "message": record.message,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_FIELDS:
                log_obj[key] = value
        return json.dumps(log_obj)


def get_logger(*, name: str, domain: Domain) -> logging.Logger:
    logger = logging.getLogger(f"toa.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter(module=name, domain=domain))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
