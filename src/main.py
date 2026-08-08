from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router


def _rebuild_schemas():
    from src.books.schemas import BookSchema, BookDetailSchema
    from src.auth.schemas import UserSchema, UserDetailSchema
    from src.reviews.schemas import ReviewSchema, ReviewDetailSchema

    ReviewSchema.model_rebuild(
        _types_namespace={"UserSchema": UserSchema, "BookSchema": BookSchema}
    )
    ReviewDetailSchema.model_rebuild(
        _types_namespace={"UserSchema": UserSchema, "BookSchema": BookSchema}
    )
    BookDetailSchema.model_rebuild(
        _types_namespace={"ReviewSchema": ReviewSchema}
    )
    UserDetailSchema.model_rebuild(
        _types_namespace={"BookSchema": BookSchema, "ReviewSchema": ReviewSchema}
    )


_rebuild_schemas()


# @asynccontextmanager
# async def lifespan(_app: FastAPI):
#     await init_db()
#     yield


app = FastAPI(root_path="/api/v1", description="A test api")

app.include_router(book_router, prefix="/books")
app.include_router(auth_router, prefix="/auth")
app.include_router(review_router, prefix="/reviews")


@app.get("/health", status_code=200)
async def get_health():
    return {"message": "All working fine!"}


# @app.get("/get-headers", status_code=status.HTTP_200_OK)
# async def get_headers(request: Request, user_agent: Annotated[str | None, Header()] = None):
#     return {"headers": request.headers, "user-agent": user_agent, "cookies": request.cookies}
