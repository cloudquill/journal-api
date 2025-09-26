import inspect
import logging
from functools import wraps

from azure.cosmos.exceptions import (
    CosmosHttpResponseError, 
    CosmosResourceNotFoundError
)

from exceptions import EntryNotFoundError

logger = logging.getLogger("journal")

def handle_cosmos_exception(error_msg: str):
    """
    Handles Cosmos DB exceptions with custom messages and logging.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (CosmosHttpResponseError, CosmosResourceNotFoundError) as e:
                log_extra = {}

                # Trying to remove guesswork by binding argument names to their values
                # and accessing them.
                sig = inspect.signature(func)

                # Bind the arguments to the parameters
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                log_extra = {
                    name: value
                    for name, value in bound_args.arguments.items()
                    if name != 'self'
                }

                if log_extra:
                    logger.exception(
                        "Couldn't %s %s. Details: %s", 
                        error_msg, 
                        log_extra, 
                        str(e)
                    )
                else:
                    logger.exception(
                        "Couldn't %s. Details: %s", 
                        error_msg, 
                        str(e)
                    )
                raise e
        return wrapper
    return decorator

def log_service_call(error_msg: str):
        """
        Logs results and errors of methods in EntryService.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                log_extra = {}
                
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                log_extra = {
                    name: value
                    for name, value in bound_args.arguments.items()
                    if name != 'self'
                }
                
                try:
                    return await func(*args, **kwargs)
                except (CosmosHttpResponseError, CosmosResourceNotFoundError) as e:
                    if e.status_code == 404:
                        logger.warning("Couldn't %s. Details: %s", error_msg, log_extra)
                        raise EntryNotFoundError("Entry not found.") from e
                    else:
                        logger.exception(
                            "Couldnt %s: %s", 
                            error_msg, 
                            str(e)
                        )
                        raise e
            return wrapper
        return decorator