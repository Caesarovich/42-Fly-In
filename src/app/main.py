import logging
import sys

from src.app.screen.loading_screen import LoadingScreen

from .app import App
from .args import AppConfig, parse_args
from .logging_utils import configure_logging

logger = logging.getLogger(__name__)


def main(config: AppConfig) -> None:
    configure_logging()

    logger.info("Starting application")
    app = App(config)
    try:
        app.load_screen(LoadingScreen(app))
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error loading maps: {e}")
        sys.exit(1)
    logger.info("Running application")
    app.run()


if __name__ == "__main__":
    try:
        args = parse_args()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error parsing command-line arguments: {e}")
        sys.exit(1)

    try:
        main(args)
    except Exception as e:  # noqa: BLE001
        logger.fatal(
            f"Application crashed with an unhandled exception: {e}", exc_info=True
        )
        sys.exit(1)
