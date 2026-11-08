"""Belge işleme işçisi. A3'e kadar yalnız kuyruğu bekleyen döngüdür."""

import logging
import signal
import threading

from visual_agent.settings import Settings

logger = logging.getLogger(__name__)


def run_worker(stop: threading.Event, poll_seconds: float) -> int:
    """Durdurulana kadar bekler; tamamlanan bekleme sayısını döndürür."""
    polls = 0
    while not stop.wait(poll_seconds):
        polls += 1
    return polls


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    stop = threading.Event()

    def request_stop(signum: int, _frame: object) -> None:
        logger.info("Durdurma sinyali alındı: %s", signal.Signals(signum).name)
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logger.info("İşçi başladı")
    run_worker(stop, settings.worker_poll_seconds)
    logger.info("İşçi durdu")


if __name__ == "__main__":
    main()
