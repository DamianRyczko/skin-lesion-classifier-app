"""Terminal logging: run the site and watch what it does.

Modules import `logger` from loguru directly. Each event carries a short
session id, so parallel browser tabs stay readable. Set LOG_LEVEL=DEBUG to
also see each TTA view.
"""

import os
import sys
from typing import TYPE_CHECKING

from loguru import logger
from streamlit.runtime.scriptrunner import get_script_run_ctx

if TYPE_CHECKING:
    from loguru import Record

FORMAT = "<green>{time:HH:mm:ss}</green> <level>{level: <7}</level> <cyan>{extra[sid]: <6}</cyan> <level>{message}</level>"

_configured = False


def _add_session_id(record: Record) -> None:
    """Read at log time, so widget callbacks (which run before the script) get it too."""
    ctx = get_script_run_ctx(suppress_warning=True)
    record["extra"]["sid"] = ctx.session_id[:6] if ctx else "-"


def setup_logging() -> None:
    """Configure once; Streamlit reruns app.py on every interaction."""
    global _configured
    if _configured:
        return
    logger.remove()
    logger.configure(patcher=_add_session_id)
    logger.add(sys.stderr, format=FORMAT, level=os.getenv("LOG_LEVEL", "INFO").upper(), colorize=True)
    _configured = True
