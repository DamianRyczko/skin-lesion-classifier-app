from loguru import logger

from core import log


def test_setup_runs_once_and_events_get_a_session_id():
    log.setup_logging()
    log.setup_logging()
    lines = []
    sink = logger.add(lambda message: lines.append(message.record["extra"]["sid"]), format="{message}")
    logger.info("hello")
    logger.remove(sink)
    assert lines == ["-"]  # outside a Streamlit session
