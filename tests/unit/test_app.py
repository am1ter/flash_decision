import contextlib
import io
import json
import os
import re
import sys
from contextlib import contextmanager
from typing import Generator
from unittest import TestCase, main, mock

from flash_backend.app.logger import UvicornCustomFormatter, create_logger


class TestLogs(TestCase):
    @contextmanager
    def _prod_stderr_simulation(self) -> Generator[None, None, None]:
        """Use context manager for simulation not atty console (docker-like)"""
        orig_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            yield
        finally:
            sys.stderr = orig_stderr

    def _capture_stdout_log_msg(self) -> str:
        """Temporary replace stdout with IO object, send"""
        logger = create_logger()
        log_text_io = io.StringIO()
        with contextlib.redirect_stdout(log_text_io):
            logger.info("test_logs", custom="custom message")
        log_text_str = log_text_io.getvalue()
        return log_text_str

    def _clean_log_msg(self, log_msg: str) -> str:
        ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        log_text_str_clean = ansi_escape.sub("", log_msg)
        return log_text_str_clean

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_app_dev(self) -> None:
        """Test pretty printing for dev env"""
        # Capture stdout messages
        log_text_str = self._capture_stdout_log_msg()

        # Use regular expression to remove non-ANSI symbols
        log_text_str_clean = self._clean_log_msg(log_text_str)

        # Make check
        expected_words = ["[info", "test_logs", "custom=custom message"]
        for word in expected_words:
            self.assertIn(word, log_text_str_clean)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_app_prod(self) -> None:
        """Test structured output for prod env"""
        # Simulate production env (for example, docker-like)
        with self._prod_stderr_simulation():
            # Capture stdout messages
            log_text_str = self._capture_stdout_log_msg()

            # Make check
            expected = {"level": "info", "event": "test_logs", "custom": "custom message"}
            self.assertDictContainsSubset(expected, json.loads(log_text_str))

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_uvicorn_dev(self) -> None:
        """Test pretty printing for dev env"""
        formatter = UvicornCustomFormatter()
        log_msg = "2000-01-01 00:00:00,000 [\x1b[32mINFO\x1b[0m:    ] Will watch for changes:[]"
        log_msg_fmt = formatter.formatMessage(log_msg)
        log_msg_fmt_clean = self._clean_log_msg(log_msg_fmt)
        expected = "2000-01-01 00:00:00,000 [info     ] Will watch for changes:[]"
        self.assertEqual(log_msg_fmt_clean, expected)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_uvicorn_prod(self) -> None:
        """Test pretty printing for dev env"""
        # Simulate production env (for example, docker-like)
        with self._prod_stderr_simulation():
            formatter = UvicornCustomFormatter()
            log_msg = "2000-01-01 00:00:00,000 [\x1b[32mINFO\x1b[0m:    ] Will watch for changes:[]"
            log_msg_fmt = formatter.formatMessage(log_msg)
            log_msg_fmt_dict = json.loads(log_msg_fmt.replace("'", '"'))
            expected = {
                "event": "Will watch for changes:[]",
                "level": "info",
                "level_number": 20,
                "timestamp": "2000-01-01 00:00:00,000",
            }
            self.assertDictContainsSubset(expected, log_msg_fmt_dict)


if __name__ == "__main__":
    main()
