from fastapi import FastAPI
from app.routes import router


app = FastAPI(title="Diaper Counter API")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"Message": "Välkommen till Diaper Counter API! Gå till /docs för att testa"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

