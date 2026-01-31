import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

logger = logging.getLogger(__name__)

mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def init_mongo() -> None:
    global mongo_client, mongo_db
    uri = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
    db_name = os.getenv("MONGODB_DB", "cybersentinel")
    try:
        mongo_client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        await mongo_client.admin.command('ping')
        mongo_db = mongo_client[db_name]
        await ensure_indexes()
        logger.info(f"✅ MongoDB connected successfully at {uri}")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}. Application will use CSV data fallback.")
        mongo_client = None
        mongo_db = None


async def close_mongo() -> None:
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


def incidents_collection() -> Optional[AsyncIOMotorCollection]:
    if mongo_db is None:
        logger.warning("MongoDB not initialized, data operations will use fallback")
        return None
    return mongo_db["incidents"]


async def ensure_indexes() -> None:
    if mongo_db is None:
        return
    try:
        col = incidents_collection()
        if col:
            await col.create_index("category")
            await col.create_index("timestamp")
            await col.create_index("location")
            logger.info("Indexes created successfully")
    except Exception as e:
        logger.warning(f"Could not create indexes: {e}")


def connect_db() -> None:
    """Sync-friendly wrapper to initialize MongoDB connection.

    This attempts to run the async init_mongo appropriately depending on
    whether an event loop is already running (useful for FastAPI startup hooks).
    """
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # If an event loop is already running, schedule init_mongo as a background task
            loop.create_task(init_mongo())
            logger.info("Scheduled async MongoDB init (event loop already running)")
        except RuntimeError:
            # No event loop running, run synchronously
            asyncio.run(init_mongo())
            logger.info("MongoDB initialized via asyncio.run")
    except Exception as e:
        logger.warning(f"connect_db encountered an error: {e}")


