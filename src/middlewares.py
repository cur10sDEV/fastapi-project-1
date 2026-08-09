import logging
import math
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# disable the default logger
logger = logging.getLogger("uvicorn.access")
logger.disabled = True

RESET = "\033[0m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def register_middlewares(app: FastAPI):

    # ORDERING MATTERS - KEEP THAT IN MIND

    # add reusable custom middleware class
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def custom_logger(request: Request, call_next):
        start = time.perf_counter()

        endpoint_response = await call_next(request)

        response_time = math.ceil((time.perf_counter() - start) * 1000)

        print(
            f"{CYAN}{request.client.host}:{request.client.port}{RESET} | "
            f"{MAGENTA}{request.method}{RESET} | "
            f"{BLUE}{request.url.path}{RESET} | "
            f"{GREEN}{endpoint_response.status_code}{RESET} | "
            f"{YELLOW}{response_time}ms{RESET}"
        )

        return endpoint_response
