import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def init_mongo() -> None:
    global mongo_client, mongo_db
    uri = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
    db_name = os.getenv("MONGODB_DB", "cybersentinel")
    mongo_client = AsyncIOMotorClient(uri)
    mongo_db = mongo_client[db_name]
    await ensure_indexes()


async def close_mongo() -> None:
    global mongo_client
    if mongo_client:
        mongo_client.close()


def incidents_collection() -> AsyncIOMotorCollection:
    assert mongo_db is not None, "MongoDB is not initialized"
    return mongo_db["incidents"]


async def ensure_indexes() -> None:
    col = incidents_collection()
    await col.create_index("category")
    await col.create_index("timestamp")
    await col.create_index("location")


