from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import certifi
import io
import pandas as pd
import datetime

client = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI, tlsCAFile=certifi.where())
    db = client[settings.MONGO_DB]


async def close_mongo_connection():
    client.close()


async def save_prediction(student_data: dict, prediction: dict):
    collection = db["predictions"]
    await collection.insert_one(
        {**student_data, "prediction": prediction, "timestamp": datetime.utcnow()}
    )


async def upload_training_data(file_content: bytes):
    collection = db["training_data"]
    df = pd.read_csv(io.BytesIO(file_content))
    await collection.insert_many(df.to_dict("records"))


async def get_new_training_data():
    collection = db["training_data"]
    return await collection.find({"processed": False}).to_list(None)


async def mark_data_as_processed(data):
    collection = db["training_data"]
    ids = [item["_id"] for item in data]
    await collection.update_many({"_id": {"$in": ids}}, {"$set": {"processed": True}})
