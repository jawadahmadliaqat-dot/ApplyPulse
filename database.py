import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_DETAILS)

# Database Reference (Both aliases for safety)
db = client.applypulse_db
database = db

# Collections
users_collection = db.get_collection("users")
jobs_collection = db.get_collection("jobs")


async def remove_duplicate_jobs() -> int:
	"""Keep the oldest copy before creating the unique ownership index."""
	duplicates_removed = 0
	pipeline = [
		{
			"$match": {
				"user_id": {"$exists": True, "$ne": None},
				"job_url": {"$exists": True, "$ne": None},
			}
		},
		{"$sort": {"created_at": 1, "_id": 1}},
		{
			"$group": {
				"_id": {"user_id": "$user_id", "job_url": "$job_url"},
				"job_ids": {"$push": "$_id"},
			}
		},
		{"$match": {"$expr": {"$gt": [{"$size": "$job_ids"}, 1]}}},
	]

	async for duplicate_group in jobs_collection.aggregate(pipeline):
		duplicate_ids = duplicate_group["job_ids"][1:]
		if duplicate_ids:
			result = await jobs_collection.delete_many({"_id": {"$in": duplicate_ids}})
			duplicates_removed += result.deleted_count
	return duplicates_removed


async def ensure_indexes() -> None:
	"""Create indexes used by ownership filtering and duplicate prevention."""
	await remove_duplicate_jobs()
	await users_collection.create_index("email", unique=True)
	await jobs_collection.create_index([("user_id", 1), ("job_url", 1)], sparse=True, unique=True)
	await jobs_collection.create_index([("user_id", 1), ("created_at", -1)])