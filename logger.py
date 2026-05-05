import os
import logging
from .handlers import JsonFileHandler, N8NHandler
from .filters import N8NFilter
from .levels import register

from pathlib import Path
import os
import platform


def _default_base_dir():
    # prioridade 1: variável de ambiente
    env_path = os.getenv("ROBOT_LOG_DIR")
    if env_path:
        return Path(env_path)

    # prioridade 2: Linux padrão (/dados)
    if Path("/dados").exists():
        return Path("/dados/logs")

    # prioridade 3: diretório do usuário (cross-platform)
    return Path.home() / "robot_logs"


def _resolve_dirs(log_dir=None, json_dir=None):
    base = _default_base_dir()

    log_dir = Path(log_dir) if log_dir else base
    json_dir = Path(json_dir) if json_dir else base / "24hrs"

    return log_dir, json_dir


def setup_logger(
    robot_name,
    log_dir=None,
    json_dir=None,
    webhook_url=None,
    job_id=None,
    level=logging.INFO,
):
    register()

    log_dir, json_dir = _resolve_dirs(log_dir, json_dir)

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    logger = logging.getLogger(f"robot.{robot_name}")
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        logger.handlers.clear()

    log_file = log_dir / f"{robot_name}.log"
    json_file = json_dir / f"{robot_name}.jsonl"

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    json_handler = JsonFileHandler(json_file)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(json_handler)

    if webhook_url:
        n8n_handler = N8NHandler(webhook_url, job_id)
        n8n_handler.addFilter(N8NFilter())
        logger.addHandler(n8n_handler)

    return logger