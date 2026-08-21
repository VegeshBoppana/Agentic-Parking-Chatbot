import logging
import sys

from shared.config import ENV

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.DEBUG if ENV == "development" else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    for noisy in ("openai", "httpx", "httpcore", "trulens", "alembic"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(name)