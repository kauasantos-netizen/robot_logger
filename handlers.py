import logging
import json
import socket
import requests
import traceback
import time
import sys
from datetime import datetime
from pathlib import Path


class JsonFileHandler(logging.Handler):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def emit(self, record):
        try:
            payload = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "function_module": record.module,
                "funcName": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                payload["exception"] = "".join(traceback.format_exception(*record.exc_info))

            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

        except Exception:
            self.handleError(record)


class N8NHandler(logging.Handler):
    def __init__(self, webhook_url, job_id=None):
        super().__init__()
        self.webhook_url = webhook_url
        self.job_id = job_id

    def emit(self, record):
        try:
            payload = {
                "jobId": self.job_id,
                "status": self._map_level(record.levelname),

                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "logger": record.name,
                "message": record.getMessage(),

                "main_module": self._get_main_module(),
                "function_module": record.module,
                "funcName": record.funcName,
                "line": record.lineno,

                "host": socket.gethostname()
            }

            if record.exc_info:
                payload["exception"] = "".join(traceback.format_exception(*record.exc_info))

            for attempt in range(3):
                try:
                    requests.post(self.webhook_url, json=payload, timeout=5)
                    break
                except Exception:
                    if attempt < 2:
                        time.sleep(2)

        except Exception:
            self.handleError(record)

    def _map_level(self, level):
        return {
            "WARNING": "warning",
            "ERROR": "error",
            "END": "success"
        }.get(level, "running")

    def _get_main_module(self):
        try:
            main_file = sys.modules["__main__"].__file__
            if main_file:
                return Path(main_file).stem
        except Exception:
            pass
        return "unknown"