from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(root_path="/api/v1", description="A test api")

app.include_router(book_router, prefix="/books")
app.include_router(auth_router, prefix="/auth")


@app.get("/health", status_code=200)
async def get_health():
    return {"message": "All working fine!"}


# @app.get("/get-headers", status_code=status.HTTP_200_OK)
# async def get_headers(request: Request, user_agent: Annotated[str | None, Header()] = None):
#     return {"headers": request.headers, "user-agent": user_agent, "cookies": request.cookies}
