from fastapi import FastAPI
from app.routes import router
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(current_dir, "static")

app = FastAPI(title="Diaper Counter API")
app.include_router(router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", include_in_schema=False)
def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

