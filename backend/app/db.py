from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import certifi
import io
import pandas as pd
import datetime
import logging
from typing import Optional, List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
client: Optional[AsyncIOMotorClient] = None
db = None

# Define required collections to ensure they exist
REQUIRED_COLLECTIONS = ["predictions", "training_data", "training_metrics", "status"]


async def connect_to_mongo():
    """
    Connect to MongoDB and initialize collections.

    Returns:
        bool: True if connection successful, False otherwise
    """
    global client, db

    # If already connected, return True
    if client is not None and db is not None:
        try:
            # Quick ping to check connection is still alive
            await db.command("ping")
            logger.debug("Using existing MongoDB connection")
            return True
        except Exception:
            # Connection was dropped, try to reconnect
            logger.info("MongoDB connection was dropped, reconnecting...")
            # Continue with reconnection process

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
        await ensure_collections_exist()

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
            db = None

        # Return False to indicate failed connection
        return False


async def ensure_collections_exist():
    """Ensure all required collections exist in the database."""
    global db
    if db is None:
        logger.error("Cannot ensure collections exist: No active database connection")
        return False

    try:
        collections = await db.list_collection_names()

        for collection in REQUIRED_COLLECTIONS:
            if collection not in collections:
                logger.info(f"Creating missing collection: {collection}")
                await db.create_collection(collection)

                # Initialize status collection with a default document
                if collection == "status":
                    await db["status"].insert_one(
                        {
                            "_id": "retraining",
                            "status": "not_started",
                            "created_at": datetime.datetime.utcnow(),
                        }
                    )

        return True
    except Exception as e:
        logger.error(f"Failed to ensure collections exist: {str(e)}")
        return False


async def close_mongo_connection():
    """Close the MongoDB connection if it exists."""
    global client, db
    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None
        db = None


async def get_db():
    """
    Get the database connection, ensuring it's connected first.

    Returns:
        MongoDB database object or None if connection failed
    """
    global db
    if await is_connected():
        return db

    if await connect_to_mongo():
        return db

    return None


async def is_connected():
    """Check if MongoDB is connected.

    Returns:
        bool: True if connected, False otherwise
    """
    global client, db
    if client is None or db is None:
        return False

    try:
        # Test connection with ping
        await db.command("ping")
        return True
    except Exception:
        return False


async def save_prediction(student_data: dict, prediction: dict):
    """Save a prediction to the database.

    Args:
        student_data: Student information
        prediction: Prediction results

    Returns:
        ObjectId: ID of inserted document or None if failed
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot save prediction: No database connection")
                return None

        collection = db["predictions"]
        document = {
            **student_data,
            "prediction": prediction,
            "timestamp": datetime.datetime.utcnow(),
        }
        result = await collection.insert_one(document)
        logger.debug(f"Saved prediction with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error saving prediction: {str(e)}")
        return None


async def upload_training_data(file_content: bytes):
    """Upload training data from CSV file.

    Args:
        file_content: Binary CSV content

    Returns:
        int: Number of inserted records
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot upload training data: No database connection")
                raise ConnectionError("Database connection unavailable")

        collection = db["training_data"]
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
    """Get unprocessed training data.

    Returns:
        list: List of unprocessed training records
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot get training data: No database connection")
                return []

        collection = db["training_data"]
        cursor = collection.find({"processed": False})
        data = await cursor.to_list(length=None)
        logging.info(f"Found {len(data)} unprocessed training records")
        return data
    except Exception as e:
        logging.error(f"Error fetching new training data: {str(e)}")
        return []


async def mark_data_as_processed(data):
    """Mark data as processed.

    Args:
        data: List of data documents to mark

    Returns:
        int: Number of updated documents
    """
    global db
    if not data:
        return 0

    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot mark data as processed: No database connection")
                return 0

        collection = db["training_data"]
        ids = [item["_id"] for item in data]
        result = await collection.update_many(
            {"_id": {"$in": ids}},
            {"$set": {"processed": True, "processed_at": datetime.datetime.utcnow()}},
        )
        logger.info(f"Marked {result.modified_count} records as processed")
        return result.modified_count
    except Exception as e:
        logger.error(f"Error marking data as processed: {str(e)}")
        return 0


async def save_training_metrics(metrics, timestamp=None):
    """Save training metrics to database.

    Args:
        metrics: Dictionary of training metrics
        timestamp: Optional timestamp, defaults to current time

    Returns:
        ID of inserted document
    """
    global db
    if not timestamp:
        timestamp = datetime.datetime.utcnow()

    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot save training metrics: No database connection")
                return None

        collection = db["training_metrics"]
        document = {
            "metrics": metrics,
            "timestamp": timestamp,
            "data_points": (
                metrics.get("data_points", 0) if isinstance(metrics, dict) else 0
            ),
        }
        result = await collection.insert_one(document)
        logger.info(f"Saved training metrics with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error saving training metrics: {str(e)}")
        return None


async def get_latest_training_metrics():
    """Get the most recent training metrics.

    Returns:
        Dictionary with metrics or None if no metrics exist
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot get training metrics: No database connection")
                return None

        collection = db["training_metrics"]
        result = await collection.find_one(sort=[("timestamp", -1)])
        return result
    except Exception as e:
        logger.error(f"Error fetching training metrics: {str(e)}")
        return None


async def update_retraining_status(status: str, additional_data: Dict[str, Any] = None):
    """Update the retraining status.

    Args:
        status: Status string (e.g., "in_progress", "completed", "failed")
        additional_data: Additional data to include in the status document

    Returns:
        bool: True if successful, False otherwise
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot update retraining status: No database connection")
                return False

        # Create base update document with timestamp
        now = datetime.datetime.utcnow()
        update_doc = {"$set": {"status": status, "updated_at": now}}

        # Add timestamp field specific to the status
        if status == "in_progress":
            update_doc["$set"]["started_at"] = now
        elif status == "completed":
            update_doc["$set"]["completed_at"] = now
        elif status == "failed":
            update_doc["$set"]["failed_at"] = now

        # Add any additional data
        if additional_data:
            for key, value in additional_data.items():
                update_doc["$set"][key] = value

        # Update the document
        collection = db["status"]
        result = await collection.update_one(
            {"_id": "retraining"}, update_doc, upsert=True
        )

        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error updating retraining status: {str(e)}")
        return False


async def get_retraining_status():
    """Get the current retraining status.

    Returns:
        dict: Status document or default status if not found
    """
    global db
    try:
        if db is None:
            if not await connect_to_mongo():
                logger.error("Cannot get retraining status: No database connection")
                return {"status": "not_started", "message": "Database not connected"}

        collection = db["status"]
        status_doc = await collection.find_one({"_id": "retraining"})

        if not status_doc:
            return {"status": "not_started"}

        return status_doc
    except Exception as e:
        logger.error(f"Error fetching retraining status: {str(e)}")
        return {"status": "not_started", "error": str(e)}
