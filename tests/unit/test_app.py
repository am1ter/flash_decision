import contextlib
import io
import json
import os
import re
import sys
from unittest import TestCase, mock

from flash_backend.app import create_logger


class TestLogs(TestCase):
    def _capture_stdout_log_msg(self) -> str:
        """Temporary replace stdout with IO object, send"""
        logger = create_logger()
        log_text_io = io.StringIO()
        with contextlib.redirect_stdout(log_text_io):
            logger.info("test_logs", custom="custom message")
        log_text_str = log_text_io.getvalue()
        return log_text_str

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_logs_dev(self) -> None:
        """Test pretty printing for dev env"""
        # Capture stdout messages
        log_text_str = self._capture_stdout_log_msg()

        # Use regular expression to remove non-ANSI symbols
        ansi_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        log_text_str_clean = ansi_escape.sub("", log_text_str)

        # Make check
        expected_words = ["[info", "test_logs", "custom=custom message"]
        for word in expected_words:
            self.assertIn(word, log_text_str_clean)

    @mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_logs_prod(self) -> None:
        """Test structured output for prod env"""
        # Simulate production env (for example, docker-like)
        sys.stderr = io.StringIO()

        # Capture stdout messages
        log_text_str = self._capture_stdout_log_msg()

        # Make check
        expected = {"level": "info", "event": "test_logs", "custom": "custom message"}
        self.assertDictContainsSubset(expected, json.loads(log_text_str))
