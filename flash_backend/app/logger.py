import sys

import click
import structlog
from rich.traceback import install


def create_logger() -> structlog.stdlib.BoundLogger:
    processors_shared: list[structlog.Processor] = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]
    processors_mode: list[structlog.Processor]
    if sys.stderr.isatty():
        processors_mode = [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors_mode = [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    structlog.configure(processors=processors_shared + processors_mode)
    return structlog.get_logger()


install(show_locals=True, suppress=[click])
logger = create_logger()
