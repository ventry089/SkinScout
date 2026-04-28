import asyncio
import sys
from loguru import logger

from config import LOG_FILE, LOG_LEVEL
from core.orchestrator import main


logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                  "<level>{level: <8}</level> | <cyan>{message}</cyan>")
logger.add(LOG_FILE, rotation="10 MB", retention="7 days", level="DEBUG")


if __name__ == "__main__":
    logger.info("skinscout arbitrage scanner starting")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("shutdown requested")
