"""Database utility routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/status")
def database_status(db: Session = Depends(get_db)) -> dict[str, str | int]:
    try:
        result = db.execute(text("SELECT 1 AS connection_test"))
        value = result.scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed. Check SQL Server name, database name, ODBC driver, and .env DATABASE_URL.",
        ) from exc

    return {"status": "connected", "connection_test": value}
