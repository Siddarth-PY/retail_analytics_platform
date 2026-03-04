from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://mongodb:27017"

client = AsyncIOMotorClient(MONGO_URL)

db = client["retail_analytics"]

inventory_collection = db["inventory_snapshots"]