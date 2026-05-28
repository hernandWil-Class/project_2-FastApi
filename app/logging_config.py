import logging
import sys

from pythonjsonlogger import jsonlogger


def configure_logging(level: str) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(method)s %(path)s "
        "%(status_code)s %(latency_ms)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
