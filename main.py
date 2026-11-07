from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import get_engine

app = FastAPI(title="Balance Social Service", version="0.1.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hola, mundo"}


@app.get("/health/database", response_model=bool, responses={503: {"model": bool}})
def database_health() -> bool | JSONResponse:
    try:
        with get_engine().connect() as connection:
            if connection.scalar(text("SELECT 1")) == 1:
                return True
    except (SQLAlchemyError, ValidationError):
        pass
    return JSONResponse(content=False, status_code=503)
