from typing import List

import uvicorn as uvicorn
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from memory import Memory
from settings import settings
from webapp.routes import router


memory = Memory.getInstance()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    responses={
        401: {
            "description": "Not authenticated.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        }
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.APP_BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


if settings.SWAGGER_UI:
    app.openapi = custom_openapi


EXEMPT_URLS: List[str] = ["/health/", "/favicon.ico", "/docs", "/openapi.json"]


@app.middleware("http")
async def token_auth_middleware(request: Request, call_next):
    if request.url.path in EXEMPT_URLS:
        response = await call_next(request)
        return response

    token = request.headers.get("Authorization")

    if not token or token != settings.FIX_TOKEN:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    response = await call_next(request)

    return response


if __name__ == "__main__":
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["loggers"] = {
        "": {"handlers": ["default"], "level": "INFO"},
    }
    uvicorn.run("app:app", port=8005, reload=False, log_config=uvicorn_log_config)
