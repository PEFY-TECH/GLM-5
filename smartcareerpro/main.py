import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from smartcareerpro.api.routes import router
from smartcareerpro.config import config

app = FastAPI(
    title="SmartCareerPro",
    description="AI-powered career intelligence platform powered by GLM-5",
    version="1.0.0",
)

app.include_router(router)

_static = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(os.path.join(_static, "index.html"))


if __name__ == "__main__":
    uvicorn.run(
        "smartcareerpro.main:app",
        host=config.host,
        port=config.port,
        reload=True,
    )
