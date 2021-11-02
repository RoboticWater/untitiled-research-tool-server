from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

from datetime import datetime

from .helpers import make_dict

db_client: AsyncIOMotorClient = None
database = None
note_collection = None
MONGO_DETAILS = config('MONGO_DETAILS')


async def get_db_client() -> AsyncIOMotorClient:
    """Return database client instance."""
    return db_client


async def connect_db():
    """Create database connection."""
    global db_client, database, note_collection
    db_client = AsyncIOMotorClient(MONGO_DETAILS)
    database = db_client.untitled_research_tool
    note_collection = database.get_collection('notes_collection')


async def close_db():
    """Close database connection."""
    db_client.close()
