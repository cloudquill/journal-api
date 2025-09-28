import atexit
import json
import logging
from pathlib import Path

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

from controllers import login_router, journal_router
from logging_configs import mylogger
from exceptions import (
    EntryNotFoundError,
    WeakPassword, 
    IncorrectCredentials, 
    UserAlreadyExists
)


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
async def not_found_handler(request: Request, exc: EntryNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )

@app.exception_handler(WeakPassword)
async def weak_password_handler(request: Request, exc: WeakPassword):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)}
    )

@app.exception_handler(IncorrectCredentials)
async def incorrect_authentication_handler(
        request: Request, 
        exc: IncorrectCredentials
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": str(exc)}
    )

@app.exception_handler(UserAlreadyExists)
async def taken_username_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": str(exc)}
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.error("Something unexpected happened: %s", exc, exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred. Please try again later."}
    )


app.include_router(login_router.router)
app.include_router(journal_router.router)