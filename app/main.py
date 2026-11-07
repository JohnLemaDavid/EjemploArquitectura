from fastapi import FastAPI
from app.modules.usuarios.router import router as usuarios_router
from app.routers.health import router as health_router

app = FastAPI(title="Balance Social Service", version="0.1.0")
app.include_router(health_router)
app.include_router(usuarios_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hola, mundo"}


