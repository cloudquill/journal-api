import atexit
import json
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from controllers import journal_router
from exceptions import EntryNotFoundError, JournalError


def setup_logging(config_path='logging_configs/config.json'):
    config_dir = Path(__file__).resolve().parent
    config_path = config_dir / config_path

    if config_path.exists():
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        with open(config_path, 'rt') as f: 
            logging.config.dictConfig(json.load(f))
        
        # Because the queue_handler is starting a thread, this doesn't
        # happen automatically. Manually start a thread
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning("Log configuration file not found. Using basic configuration.")


setup_logging()
logger = logging.getLogger("journal")
logger.info("Opening Journal")

app = FastAPI()

@app.exception_handler(EntryNotFoundError)
async def not_found_exception_handler(request, exc: EntryNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )


@app.exception_handler(JournalError)
async def unexpected_error_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


app.include_router(journal_router.router)