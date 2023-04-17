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
from unittest import TestCase, main, mock

from flash_backend.app.logger import (
    UvicornCustomDefaultFormatter,
    UvicornCustomFormatterAccess,
    create_logger,
)


class TestLogs(TestCase):
    @contextmanager
    def _prod_stdout_simulation(self) -> Generator[None, None, None]:
        """Use context manager for simulation not atty console (docker-like)"""

        orig_stdout = sys.stdout
        try:
            sys.stdout = io.StringIO()
            yield
        finally:
            sys.stdout = orig_stdout

    def _capture_stdout_log_msg(self) -> str:
        """Temporary replace stdout with IO object, send"""

        # New logger must be created, because it might be not atty during the test
        logger = create_logger()
        log_text_io = io.StringIO()
        handler = logging.StreamHandler(log_text_io)
        logger.addHandler(handler)
        logger.info("test_logs", custom="custom message")
        log_text_str = log_text_io.getvalue()
        return log_text_str

    def _clean_log_msg(self, log_msg: str) -> str:
        """Remove style tags from msg (color, weight, etc)"""

        ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        log_text_str_clean = ansi_escape.sub("", log_msg)
        return log_text_str_clean

    def _create_mock_log_record_app(self, msg: str) -> LogRecord:
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

    def _create_mock_log_record_uvicorn(self) -> LogRecord:
        attrs_access = {
            "client_addr": "127.0.0.1:43136",
            "method": "GET",
            "full_path": "/",
            "http_version": "1.1",
            "status_code": 200,
        }
        log_msg = " %s | \x1b[1m%s %s HTTP/%s\x1b[0m | \x1b[32m%d OK\x1b[0m"
        log_msg_fill = log_msg % tuple(attrs_access.values())
        mock_record = self._create_mock_log_record_app(log_msg_fill)
        mock_record.args = tuple(attrs_access.values())
        return mock_record

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_app_dev(self) -> None:
        """Test App pretty logs for dev env"""

        # Capture stdout messages
        log_text_str = self._capture_stdout_log_msg()

        # Use regular expression to remove non-ANSI symbols
        log_text_str_clean = self._clean_log_msg(log_text_str)

        # Verify
        expected_words = ["[info", "test_logs", "custom=custom message"]
        for word in expected_words:
            self.assertIn(word, log_text_str_clean)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_app_prod(self) -> None:
        """Test App structured logs for prod env"""

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            # Capture stdout messages
            log_text_str = self._capture_stdout_log_msg()

            # Verify
            expected = {"level": "info", "event": "test_logs", "custom": "custom message"}
            self.assertDictContainsSubset(expected, json.loads(log_text_str))

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_uvicorn_dev_default(self) -> None:
        """Test Uvicorn pretty system logs for dev env"""

        formatter = UvicornCustomDefaultFormatter()

        # Create mock record
        log_msg = "2000-01-01 00:00:00,000 [\x1b[32mINFO\x1b[0m:    ] Will watch for changes:[]"
        mock_record = self._create_mock_log_record_app(log_msg)

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] Will watch for changes:[]"
        self.assertEqual(log_msg_fmt_clean, expected)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_uvicorn_prod_default(self) -> None:
        """Test Uvicorn pretty system logs for prod env"""

        # Simulate production env (for example, docker-like)
        with self._prod_stdout_simulation():
            formatter = UvicornCustomDefaultFormatter()

            # Create mock record
            log_msg = "Will watch for changes in these directories: []"
            mock_record = self._create_mock_log_record_app(log_msg)

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
    def test_logs_uvicorn_dev_access(self) -> None:
        """Test Uvicorn pretty access logs for dev env"""

        formatter = UvicornCustomFormatterAccess()

        # Create mock record with color tags
        mock_record = self._create_mock_log_record_uvicorn()

        # Format record object, delete style tags and verify it
        log_msg_fmt = formatter.formatMessage(mock_record)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] 127.0.0.1:43136 | GET / HTTP/1.1 | 200 OK"
        self.assertEqual(log_msg_fmt_clean, expected)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_uvicorn_prod_access(self) -> None:
        """Test Uvicorn pretty access logs for prod env"""

        formatter = UvicornCustomFormatterAccess()

        # Create mock record with color tags
        mock_record = self._create_mock_log_record_uvicorn()

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


if __name__ == "__main__":
    main()
