import re
import sys
from copy import deepcopy
from logging import LogRecord
from typing import Any

import click
import rich.traceback
import structlog
from structlog._log_levels import _NAME_TO_LEVEL
from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import DefaultFormatter


class UvicornCustomFormatter(DefaultFormatter):
    """Custom unicorn logger for system messages"""

    def formatMessage(self, record: LogRecord | str) -> str:
        record_source = super().formatMessage(record) if isinstance(record, LogRecord) else record
        if sys.stderr.isatty():
            # Source record has format like: [\x1b[32mINFO\x1b[0m:    ]
            regex_level = re.compile(r"[0-9]{1,2}m.*[0-9]{1,2}m:")
            # Reformat level
            try:
                level_raw = regex_level.findall(record_source)[0]
            except IndexError:
                return record_source
            level_new = level_raw.lower().replace(":", " ")
            # Update record
            record_new = regex_level.sub(level_new, record_source)
            return record_new
        else:
            ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
            record_clean = ansi_escape.sub("", record_source)
            part_date = record_clean[:23]
            part_level_name = record_clean[25:34].replace(":", " ").strip().lower()
            part_level_num = _NAME_TO_LEVEL[part_level_name]
            part_event = record_clean[36:]
            return str(
                {
                    "event": part_event,
                    "level": part_level_name,
                    "level_number": part_level_num,
                    "timestamp": part_date,
                }
            )


def create_logger() -> structlog.stdlib.BoundLogger:
    """Create structlog logger"""

    processors_shared: list[structlog.Processor] = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S,%MS", utc=False),
    ]
    processors_mode: list[structlog.Processor]
    if sys.stderr.isatty():
        processors_mode = [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors_mode = [
            structlog.stdlib.add_log_level_number,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    structlog.configure(processors=processors_shared + processors_mode)
    return structlog.get_logger()


def update_uvicorn_log_config() -> dict[str, Any]:
    """Change uvicorn log settings to conform with structlog"""

    uvicorn_log_config = deepcopy(LOGGING_CONFIG)
    fmt_access = "%(asctime)s | %(client_addr)s | %(request_line)s | %(status_code)s"
    uvicorn_log_config["formatters"]["access"]["fmt"] = fmt_access
    uvicorn_log_config["formatters"]["custom"] = {
        "()": UvicornCustomFormatter,
        "format": "%(asctime)s [%(levelprefix)s] %(message)s",
    }
    uvicorn_log_config["handlers"]["default"]["formatter"] = "custom"
    return uvicorn_log_config


rich.traceback.install(show_locals=True, suppress=[click])
logger = create_logger()
uvicorn_log_config = update_uvicorn_log_config()
