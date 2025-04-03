from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings  # Adjust import path as needed
import certifi
import io
import pandas as pd
import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
client = None
db = None


async def connect_to_mongo():
    global client, db
    try:
        # Get connection options from settings
        connection_options = settings.get_mongo_connection_options()

        # Log connection attempt
        logger.info(f"Connecting to MongoDB ({settings.ENVIRONMENT} environment)")

        # MongoDB Atlas always requires TLS
        client = AsyncIOMotorClient(
            settings.MONGODB_URI, tlsCAFile=certifi.where(), **connection_options
        )

        # Test connection with a ping command
        await client.admin.command("ping")
        server_info = await client.server_info()

        # Set the database
        db = client[settings.MONGO_DB]

        # Check if required collections exist and create if needed
        collections = await db.list_collection_names()
        required_collections = ["predictions", "training_data"]

        for collection in required_collections:
            if collection not in collections:
                logger.info(f"Creating missing collection: {collection}")
                await db.create_collection(collection)

        logger.info(
            f"Successfully connected to MongoDB {server_info.get('version', 'unknown')}"
        )
        logger.info(f"Using database: {settings.MONGO_DB}")

        # Return True to indicate successful connection
        return True

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        if client:
            client.close()
            client = None

        # Return False to indicate failed connection (instead of raising)
        return False


async def close_mongo_connection():
    if client:
        logger.info("Closing MongoDB connection")
        client.close()


async def is_connected():
    global client, db
    if client is None or db is None:
        return False
    return client is not None and db is not None


async def save_prediction(student_data: dict, prediction: dict):
    collection = db["predictions"]
    document = {
        **student_data,
        "prediction": prediction,
        "timestamp": datetime.datetime.utcnow(),
    }
    result = await collection.insert_one(document)
    logger.debug(f"Saved prediction with ID: {result.inserted_id}")
    return result.inserted_id


async def upload_training_data(file_content: bytes):
    collection = db["training_data"]

    try:
        df = pd.read_csv(io.BytesIO(file_content))

        # Validate required columns are present
        required_fields = set(settings.TRAINING_DATA_FIELDS + ["dropout_status"])
        if not required_fields.issubset(df.columns):
            missing = required_fields - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")

        # Convert DataFrame to list of dictionaries with processed flag
        records = df.to_dict("records")
        for record in records:
            record["processed"] = False
            record["uploaded_at"] = datetime.datetime.utcnow()

        # Insert records
        result = await collection.insert_many(records)
        logger.info(f"Uploaded {len(result.inserted_ids)} training records")

        return len(result.inserted_ids)

    except Exception as e:
        logger.error(f"Error uploading training data: {str(e)}")
        raise


async def get_new_training_data():
    try:
        collection = db["training_data"]
        cursor = collection.find({"processed": False})
        data = await cursor.to_list(length=None)
        logging.info(f"Found {len(data)} unprocessed training records")
        return data
    except Exception as e:
        logging.error(f"Error fetching new training data: {str(e)}")
        return []  # Return empty list instead of None


async def mark_data_as_processed(data):
    if not data:
        return 0

    collection = db["training_data"]
    ids = [item["_id"] for item in data]
    result = await collection.update_many(
        {"_id": {"$in": ids}},
        {"$set": {"processed": True, "processed_at": datetime.datetime.utcnow()}},
    )
    logger.info(f"Marked {result.modified_count} records as processed")
    return result.modified_count


async def save_training_metrics(metrics, timestamp=None):
    """Save training metrics to database

    Args:
        metrics: Dictionary of training metrics
        timestamp: Optional timestamp, defaults to current time

    Returns:
        ID of inserted document
    """
    if not timestamp:
        timestamp = datetime.datetime.utcnow()

    collection = db["training_metrics"]
    document = {"metrics": metrics, "timestamp": timestamp}
    result = await collection.insert_one(document)
    logger.info(f"Saved training metrics with ID: {result.inserted_id}")
    return result.inserted_id


async def get_latest_training_metrics():
    """Get the most recent training metrics

    Returns:
        Dictionary with metrics or None if no metrics exist
    """
    collection = db["training_metrics"]
    result = await collection.find_one(sort=[("timestamp", -1)])

    return result
