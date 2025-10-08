import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


async def _connect_to_mongo() -> AsyncIOMotorDatabase:
    """Connect to MongoDB using Motor and return the database handle."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    return db


async def _close_mongo(db: AsyncIOMotorDatabase) -> None:
    """Close MongoDB connection."""
    client: AsyncIOMotorClient = db.client
    client.close()


def _resolve_indexes_path() -> Optional[Path]:
    """Resolve the path to indexes.json using ENV or known sibling container path."""
    # Prefer explicit path from environment
    if settings.INDEXES_FILE:
        p = Path(settings.INDEXES_FILE)
        if p.exists():
            return p

    # Attempt to resolve via known repo layout: ../healthcare-connect-5348-5358/healthcare_database/indexes/indexes.json
    try:
        this_file = Path(__file__).resolve()
        project_root = this_file.parents[3]  # .../code-generation
        candidate = project_root / "healthcare-connect-5348-5358" / "healthcare_database" / "indexes" / "indexes.json"
        if candidate.exists():
            return candidate
    except Exception:  # pragma: no cover - best-effort
        pass
    return None


async def _ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Ensure MongoDB indexes based on a JSON file definition."""
    path = _resolve_indexes_path()
    if not path:
        logger.info("Indexes file not found; skipping index ensure step.")
        return

    try:
        with path.open("r", encoding="utf-8") as f:
            spec: Dict[str, Any] = json.load(f)
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to load index spec from %s: %s", path, e)
        return

    collections = spec.get("collections", {})
    for coll_name, indexes in collections.items():
        collection = db[coll_name]
        for idx in indexes:
            keys: Dict[str, int] = idx.get("keys", {})
            options: Dict[str, Any] = idx.get("options", {})
            if not keys:
                continue
            try:
                await collection.create_index(list(keys.items()), **options)
                logger.info("Ensured index on %s: %s (options=%s)", coll_name, keys, options)
            except Exception as e:  # pragma: no cover
                logger.warning("Failed to create index on %s with keys %s: %s", coll_name, keys, e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context to manage DB connection and indexes."""
    db = await _connect_to_mongo()
    app.state.db = db
    await _ensure_indexes(db)
    try:
        yield
    finally:
        await _close_mongo(db)


# PUBLIC_INTERFACE
def get_db_from_app(app: FastAPI) -> AsyncIOMotorDatabase:
    """Get a reference to the active AsyncIOMotorDatabase from FastAPI app state."""
    db: AsyncIOMotorDatabase = app.state.db
    return db
