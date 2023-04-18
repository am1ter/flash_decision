import contextlib
import io
import json
import logging
import os
import re
import sys
from contextlib import contextmanager
from logging import LogRecord
from typing import Generator
from unittest import TestCase, mock

from structlog.stdlib import BoundLogger

from flash_backend.app.logger import (
    UvicornCustomDefaultFormatter,
    UvicornCustomFormatterAccess,
    create_logger,
)


class TestLogs(TestCase):
    def _create_custom_logger(self) -> tuple[BoundLogger, io.StringIO]:
        """Create custom logger that might be used in some tests and add additional IO handler"""
        custom_logger = create_logger(f"test_{id(self)}")
        log_text_io = io.StringIO()
        handler = logging.StreamHandler(log_text_io)
        custom_logger.addHandler(handler)
        return (custom_logger, log_text_io)

    @staticmethod
    @contextmanager
    def _prod_stdout_simulation() -> Generator[None, None, None]:
        """Use context manager for simulation not tty-like console (docker-like)"""

        orig_stdout = sys.stdout
        try:
            sys.stdout = io.StringIO()
            yield
        finally:
            sys.stdout = orig_stdout

    def _capture_stdout_log_msg(self, event: str | Exception, **kwargs) -> str:
        """Temporary replace stdout with IO object, send"""

        # New logger must be created, because test require consoles with different tty-like status
        custom_logger, log_text_io = self._create_custom_logger()

        # Custom logger output to stdout and to the IO object simultaniously
        if isinstance(event, Exception):
            custom_logger.exception(str(event), **kwargs)
        else:
            custom_logger.info(event, **kwargs)

        log_text_str = log_text_io.getvalue()
        return log_text_str

    @staticmethod
    def _clean_log_msg(log_msg: str) -> str:
        """Remove style tags from msg (color, weight, etc)"""

        ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        log_text_str_clean = ansi_escape.sub("", log_msg)
        return log_text_str_clean

    @staticmethod
    def _create_mock_log_record_uvicorn_default(msg: str) -> LogRecord:
        """Create test logging.LogRecord object"""

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

    def _create_mock_log_record_uvicorn_access(self) -> LogRecord:
        attrs_access = {
            "client_addr": "127.0.0.1:43136",
            "method": "GET",
            "full_path": "/",
            "http_version": "1.1",
            "status_code": 200,
        }
        log_msg = " %s | \x1b[1m%s %s HTTP/%s\x1b[0m | \x1b[32m%d OK\x1b[0m"
        log_msg_fill = log_msg % tuple(attrs_access.values())
        mock_record = self._create_mock_log_record_uvicorn_default(log_msg_fill)
        mock_record.args = tuple(attrs_access.values())
        return mock_record

    @staticmethod
    def _create_mock_log_record_uvicorn_exception(msg: str, e: Exception) -> LogRecord:
        """Create test logging.LogRecord object"""

        ei = (type(e), e, e.__traceback__)
        mock_record = LogRecord(
            name="uvicorn.error",
            level=40,
            pathname="",
            lineno=1,
            msg=msg,
            args=None,
            exc_info=ei,
        )
        additional_attrs_any = {"asctime": "2000-01-01 00:00:00,000", "message": msg}
        mock_record.__dict__.update(additional_attrs_any)
        return mock_record

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_app_dev(self) -> None:
        """Test App pretty logs for dev env"""

        # Capture stdout messages
        log_text_str = self._capture_stdout_log_msg("test_logs", custom="custom")

        # Use regular expression to remove non-ANSI symbols
        log_text_str_clean = self._clean_log_msg(log_text_str)

        # Verify
        expected_words = ["[info", "test_logs", "custom=custom"]
        for word in expected_words:
            self.assertIn(word, log_text_str_clean)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_app_prod(self) -> None:
        """Test App structured logs for prod env"""

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            # Capture stdout messages
            log_text_str = self._capture_stdout_log_msg("test_logs", custom="custom")

            # Verify
            expected = {"level": "info", "event": "test_logs", "custom": "custom"}
            self.assertDictContainsSubset(expected, json.loads(log_text_str))

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_uvicorn_default_dev(self) -> None:
        """Test Uvicorn pretty system logs for dev env"""

        formatter = UvicornCustomDefaultFormatter()

        # Create mock record
        log_msg = "2000-01-01 00:00:00,000 [\x1b[32mINFO\x1b[0m:    ] Will watch for changes:[]"
        mock_record = self._create_mock_log_record_uvicorn_default(log_msg)

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] Will watch for changes:[]"
        self.assertEqual(log_msg_fmt_clean, expected)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_uvicorn_default_prod(self) -> None:
        """Test Uvicorn pretty system logs for prod env"""

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            formatter = UvicornCustomDefaultFormatter()

            # Create mock record
            log_msg = "Will watch for changes in these directories: []"
            mock_record = self._create_mock_log_record_uvicorn_default(log_msg)

            # Format record object, convert output string to dict and verify it
            log_msg_fmt = formatter.formatMessage(mock_record)
            log_msg_fmt_dict = json.loads(log_msg_fmt.replace("'", '"'))
            expected = {
                "event": log_msg,
                "level": "info",
                "level_number": 20,
                "timestamp": "2000-01-01 00:00:00,000",
            }
            self.assertDictContainsSubset(expected, log_msg_fmt_dict)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_uvicorn_access_dev(self) -> None:
        """Test Uvicorn pretty access logs for dev env"""

        formatter = UvicornCustomFormatterAccess()

        # Create mock record with color tags
        mock_record = self._create_mock_log_record_uvicorn_access()

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] 127.0.0.1:43136 | GET / HTTP/1.1 | 200 OK"
        self.assertEqual(log_msg_fmt_clean, expected)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_uvicorn_access_prod(self) -> None:
        """Test Uvicorn pretty access logs for prod env"""

        formatter = UvicornCustomFormatterAccess()

        # Create mock record with color tags
        mock_record = self._create_mock_log_record_uvicorn_access()

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            # Format record object, delete style tags and verify it
            log_msg_fmt = formatter.formatMessage(mock_record)
            log_msg_fmt_dict = json.loads(log_msg_fmt.replace("'", '"').replace("\\", "\\\\"))
            expected = {
                "logger": "uvicorn.default",
                "level": "info",
                "level_number": 20,
                "timestamp": "2000-01-01 00:00:00,000",
                "client_addr": "127.0.0.1:43136",
                "method": "GET",
                "full_path": "/",
                "http_version": "1.1",
                "status_code": 200,
            }
            self.assertDictContainsSubset(expected, log_msg_fmt_dict)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_exceptions_basic_dev(self) -> None:
        """Test that app use `rich` to format exception"""

        # Trigger exception
        try:
            1 / 0
        except ZeroDivisionError as e:
            # Capture stdout messages
            log_text_str = self._capture_stdout_log_msg(e)

        # Verify
        expected_words = ["ZeroDivisionError", "division by zero", self._testMethodName, "\x1b["]
        for word in expected_words:
            self.assertIn(word, log_text_str)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_exceptions_basic_prod(self) -> None:
        """Test that app format exceptions as jsons"""

        # Trigger exception
        try:
            1 / 0
        except ZeroDivisionError as e:
            # Simulate production env (for example, docker-like)
            with self._prod_stdout_simulation():
                # Capture stdout messages
                log_text_str = self._capture_stdout_log_msg(e)

        # Verify
        expected = {
            "event": "division by zero",
            "level": "error",
            "level_number": 40,
        }
        self.assertDictContainsSubset(expected, json.loads(log_text_str))

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_exceptions_uvicorn_dev(self) -> None:
        """Test Uvicorn rich exception for dev env"""

        formatter = UvicornCustomDefaultFormatter()
        try:
            1 / 0
        except ZeroDivisionError as e:
            # Create mock record
            log_msg = "Exception in ASGI application\n"
            mock_record = self._create_mock_log_record_uvicorn_exception(log_msg, e)

        # Simulate tty-like console using monkeypatching of StringIO object
        log_text_io = io.StringIO()
        log_text_io.isatty = lambda: True  # type: ignore[method-assign]

        # Catch console output
        with contextlib.redirect_stdout(log_text_io):
            formatter.format(mock_record)
        log_text_str = log_text_io.getvalue()

        # Verify
        expected_words = ["ZeroDivisionError", "division by zero", self._testMethodName, "\x1b["]
        for word in expected_words:
            self.assertIn(word, log_text_str)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_exceptions_uvicorn_prod(self) -> None:
        """Test Uvicorn rich exception for prod env"""

        try:
            1 / 0
        except ZeroDivisionError as e:
            # Create mock record
            log_msg = "Exception in ASGI application\n"
            mock_record = self._create_mock_log_record_uvicorn_exception(log_msg, e)

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            # New logger must be created, because this test require console with tty
            custom_logger, log_text_io = self._create_custom_logger()
            formatter = UvicornCustomDefaultFormatter(custom_logger=custom_logger)
            # Fomatter use custom logger which output to stdout and to the IO object simultaniously
            formatter.format(mock_record)
            log_text_str = log_text_io.getvalue()

        # Verify
        expected = {
            "event": "division by zero",
            "level": "error",
            "level_number": 40,
        }
        self.assertDictContainsSubset(expected, json.loads(log_text_str))


if __name__ == "__main__":
    TestLogs().test_exceptions_uvicorn_dev()
