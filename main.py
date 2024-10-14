import json
import logging
from fastapi import FastAPI, Response, Request
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask
from util.log_function import api_logger
from routers.nlp import nlp_router

app = FastAPI(title="Dothis Fastapi AI API server", version="1.0.0")

app.include_router(nlp_router.router)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    api_routes = [route.path for route in request.app.routes if isinstance(route, APIRoute)]
    response: Response = await call_next(request)
    async for chunk in response.body_iterator:
        res_body: dict = chunk.decode("utf-8")
    if request.url.path in api_routes:
        status_code = json.loads(res_body).get("code", 500)
        if status_code == 200:
            level = logging.INFO
        elif status_code == 500:
            level = logging.ERROR
        else:
            level = logging.WARNING
        task = BackgroundTask(api_logger, request, res_body, level)
        return Response(
            content=res_body,
            status_code=200,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task,
        )
    else:
        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

@app.get("/")
async def test():
    return {"hello": "world!"}