import contextlib
import io
import json
import re
from collections.abc import Callable
from logging import LogRecord

import attrs
import pytest
import structlog

from app.system.logger import (
    CustomStructlogLogger,
    UvicornCustomDefaultFormatter,
    UvicornCustomFormatterAccess,
    configure_logger,
)


@pytest.fixture()
def logger_dev() -> CustomStructlogLogger:
    log_text_io = io.StringIO()
    configure_logger(dev_mode=True, stream=log_text_io)
    logger = structlog.get_logger()
    logger.log_text_io = log_text_io
    return logger


@pytest.fixture()
def logger_prod() -> CustomStructlogLogger:
    log_text_io = io.StringIO()
    configure_logger(dev_mode=False, stream=log_text_io)
    logger = structlog.get_logger()
    logger.log_text_io = log_text_io
    return logger


@pytest.fixture()
def mock_log_record_uvicorn_default() -> Callable[[str], LogRecord]:
    """Create test logging.LogRecord object as uvicorn default logger message"""

    def create_mock_log_record(msg: str) -> LogRecord:
        mock_record = LogRecord(
            name="uvicorn.default",
            level=20,
            pathname="",
            lineno=1,
            msg=msg,
            args=None,
            exc_info=None,
        )
        additional_attrs_any = {"asctime": "2000-01-01 00:00:00,000", "message": msg}
        mock_record.__dict__.update(additional_attrs_any)
        return mock_record

    return create_mock_log_record


@pytest.fixture()
def mock_log_record_uvicorn_access(
    mock_log_record_uvicorn_default: Callable[[str], LogRecord]
) -> LogRecord:
    """Create test logging.LogRecord object as uvicorn access logger message"""

    attrs_access = {
        "client_addr": "127.0.0.1:43136",
        "method": "GET",
        "full_path": "/",
        "http_version": "1.1",
        "status_code": 200,
    }
    log_msg = " %s | \x1b[1m%s %s HTTP/%s\x1b[0m | \x1b[32m%d OK\x1b[0m"
    log_msg_fill = log_msg % tuple(attrs_access.values())
    mock_record = mock_log_record_uvicorn_default(log_msg_fill)
    mock_record.args = tuple(attrs_access.values())
    return mock_record


@pytest.fixture()
def mock_log_record_uvicorn_exception() -> LogRecord:
    """Create test logging.LogRecord object"""

    try:
        1 / 0  # noqa: B018
    except ZeroDivisionError as e:
        ei = (type(e), e, e.__traceback__)

    mock_record = LogRecord(
        name="uvicorn.error",
        level=40,
        pathname="",
        lineno=1,
        msg=str(ei[1]),
        args=None,
        exc_info=ei,
    )
    additional_attrs_any = {
        "asctime": "2000-01-01 00:00:00,000",
        "message": str(ei[1]),
    }
    mock_record.__dict__.update(additional_attrs_any)
    return mock_record


class TestLoggerStandartCases:
    """
    Test standart use cases for logging functions.
    Print to stdout log messages and exceptions in prod/dev modes (json- and text-formatted).
    """

    @staticmethod
    def _clean_log_msg(log_msg: str) -> str:
        """Remove style tags from msg (color, weight, etc)"""

        ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        log_text_str_clean = ansi_escape.sub("", log_msg)
        return log_text_str_clean

    def test_logs_app_dev(self, logger_dev: CustomStructlogLogger) -> None:
        """Test App pretty logs for dev env"""
        logger_dev.info("test_logs", custom="custom")

        # Verify
        expected_words = ["[1minfo", "test_logs", "[36mcustom"]
        for word in expected_words:
            assert word in logger_dev.log_text_io.getvalue()

    def test_logs_app_prod(self, logger_prod: CustomStructlogLogger) -> None:
        """Test App structured logs for prod env"""

        logger_prod.info("test_logs", custom="custom")
        log_test_dict = json.loads(logger_prod.log_text_io.getvalue())

        # Verify
        expected = {"level": "info", "message": "test_logs", "custom": "custom"}
        assert log_test_dict == log_test_dict | expected

    def test_logs_uvicorn_default_dev(
        self, mock_log_record_uvicorn_default: Callable[[str], LogRecord]
    ) -> None:
        """Test Uvicorn pretty system logs for dev env"""

        formatter = UvicornCustomDefaultFormatter(dev_mode=True)

        # Create mock record (consider if terminal supports tty or not)
        if formatter.use_colors:
            log_msg = "2000-01-01 00:00:00,000 [\x1b[32mINFO\x1b[0m:    ] Will watch for changes:[]"
        else:
            log_msg = "2000-01-01 00:00:00,000 [INFO:    ] Will watch for changes:[]"
        mock_record = mock_log_record_uvicorn_default(log_msg)

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] Will watch for changes:[]"
        assert "INFO:" not in log_msg_fmt_clean, "Reformat level func does not work"
        assert log_msg_fmt_clean == expected

    def test_logs_uvicorn_default_prod(
        self, mock_log_record_uvicorn_default: Callable[[str], LogRecord]
    ) -> None:
        """Test Uvicorn pretty system logs for prod env"""

        formatter = UvicornCustomDefaultFormatter(dev_mode=False)

        # Create mock record
        log_msg = "Will watch for changes in these directories: []"
        mock_record = mock_log_record_uvicorn_default(log_msg)

        # Format record object, convert output string to dict and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_dict = json.loads(log_msg_fmt.replace("'", '"'))
        expected = {
            "event": log_msg,
            "levelname": "info",
            "levelnumber": 20,
            "timestamp": "2000-01-01 00:00:00,000",
        }
        assert log_msg_fmt_dict == log_msg_fmt_dict | expected

    def test_logs_uvicorn_access_dev(self, mock_log_record_uvicorn_access: LogRecord) -> None:
        """Test Uvicorn pretty access logs for dev env"""

        formatter = UvicornCustomFormatterAccess(dev_mode=True)

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_log_record_uvicorn_access)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] 127.0.0.1:43136 | GET / HTTP/1.1 | 200 OK"
        assert "INFO:" not in log_msg_fmt_clean, "Reformat level func does not work"
        assert log_msg_fmt_clean == expected

    def test_logs_uvicorn_access_prod(self, mock_log_record_uvicorn_access: LogRecord) -> None:
        """Test Uvicorn pretty access logs for prod env"""

        formatter = UvicornCustomFormatterAccess(dev_mode=False)

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_log_record_uvicorn_access)
        log_msg_fmt_dict = json.loads(log_msg_fmt.replace("'", '"').replace("\\", "\\\\"))
        expected = {
            "logger": "uvicorn.default",
            "levelname": "info",
            "levelnumber": 20,
            "timestamp": "2000-01-01 00:00:00,000",
            "client_addr": "127.0.0.1:43136",
            "method": "GET",
            "full_path": "/",
            "http_version": "1.1",
            "status_code": 200,
        }
        assert log_msg_fmt_dict == log_msg_fmt_dict | expected

    def test_exceptions_basic_dev(self, logger_dev: CustomStructlogLogger) -> None:
        """Test that app use `rich` to format exception"""

        # Trigger exception
        try:
            1 / 0  # noqa: B018
        except ZeroDivisionError as e:
            logger_dev.exception(str(e))  # noqa: TRY401

        # Verify
        expected_words = [
            "ZeroDivisionError",
            "division by zero",
            "\x1b[",
        ]
        for word in expected_words:
            assert word in logger_dev.log_text_io.getvalue()

    def test_exceptions_basic_prod(self, logger_prod: CustomStructlogLogger) -> None:
        """Test that app format exceptions as jsons"""

        # Trigger exception
        try:
            1 / 0  # noqa: B018
        except ZeroDivisionError as e:
            logger_prod.exception(str(e))  # noqa: TRY401

        # Verify
        expected = {
            "levelname": "error",
            "levelnumber": 40,
        }
        log_msg_dict = json.loads(logger_prod.log_text_io.getvalue())
        assert "exception" in log_msg_dict
        assert log_msg_dict["exception"][0]["exc_type"] == ZeroDivisionError.__name__
        assert log_msg_dict == log_msg_dict | expected

    def test_exceptions_uvicorn_dev(self, mock_log_record_uvicorn_exception: LogRecord) -> None:
        """Test Uvicorn rich exception for dev env"""

        formatter = UvicornCustomDefaultFormatter(dev_mode=True)

        with contextlib.redirect_stdout(io.StringIO()) as log_text_io:
            formatter.format(mock_log_record_uvicorn_exception)
        log_text_str = log_text_io.getvalue()

        # Verify
        expected_words = ["ZeroDivisionError", "division by zero", "╭──", "╰──"]
        for word in expected_words:
            assert word in log_text_str

    def test_exceptions_uvicorn_prod(self, mock_log_record_uvicorn_exception: LogRecord) -> None:
        """Test Uvicorn rich exception for prod env"""

        formatter = UvicornCustomDefaultFormatter(dev_mode=False)

        log_text_str = formatter.format(mock_log_record_uvicorn_exception)
        log_text_dict = json.loads(log_text_str.replace("'", '"'))

        # Verify
        expected = {
            "event": "division by zero",
            "levelname": "error",
            "levelnumber": 40,
        }
        assert log_text_dict == log_text_dict | expected


@attrs.define
class FakeDomainClass:
    """Used for imitate real domain class"""

    x: str


class TestLoggerCustomCases:
    """Test custom use cases for logging functions (custom log methods, etc.)"""

    @pytest.mark.asyncio()
    async def test_info_finish_general(self, logger_prod: CustomStructlogLogger) -> None:
        """Test attribute `event` inside custom method info_finish()"""
        with structlog.testing.capture_logs() as logs:
            await logger_prod.ainfo_finish()
        excepted = {"event": "Operation completed", "log_level": "info"}
        assert logs[0] == logs[0] | excepted

    @pytest.mark.asyncio()
    async def test_info_finish_cls_name(self, logger_prod: CustomStructlogLogger) -> None:
        """Test attribute `cls` inside custom method info_finish()"""
        with structlog.testing.capture_logs() as logs:
            await logger_prod.ainfo_finish(cls=self.__class__)
        excepted = {"cls": self.__class__.__name__}
        assert logs[0] == logs[0] | excepted

    @pytest.mark.asyncio()
    async def test_info_finish_func_name(self, logger_prod: CustomStructlogLogger) -> None:
        """Test attribute `show_func_name` inside custom method info_finish()"""
        with structlog.testing.capture_logs() as logs:
            await logger_prod.ainfo_finish(show_func_name=True)
        excepted = {"function": self.test_info_finish_func_name.__name__}
        assert logs[0] == logs[0] | excepted

    @pytest.mark.asyncio()
    async def test_info_finish_domain_obj(self, logger_prod: CustomStructlogLogger) -> None:
        """Test attribute `domain_obj` inside custom method info_finish() in dev mode"""
        domain_obj = FakeDomainClass(x="test")  # type: ignore[call-arg]
        with structlog.testing.capture_logs() as logs:
            await logger_prod.ainfo_finish(domain_obj=domain_obj)
        excepted = {"domain_obj": attrs.asdict(domain_obj)}
        assert logs[0] == logs[0] | excepted
