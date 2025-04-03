from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .scripts.prediction import DropoutPredictor
from .transformation import transform_user_input
from .db import (
    connect_to_mongo,
    close_mongo_connection,
    upload_training_data,
    get_new_training_data,
    mark_data_as_processed,
    save_training_metrics,
    get_latest_training_metrics,
    db,
    client,
)
from app.schema import StudentInput, PredictionOutput, UserFriendlyInput
from app.scripts.model import DropoutModel
import pandas as pd
import logging
from app.config import settings
import datetime

app = FastAPI(
    title="Student Dropout Prediction API",
    description="API for predicting and managing student dropout risk",
    version="1.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database events
@app.on_event("startup")
async def startup():
    # Connect to MongoDB and handle connection result
    db_connected = await connect_to_mongo()
    if not db_connected:
        logging.error(
            "Failed to connect to MongoDB. Application may not function correctly."
        )
    else:
        logging.info("MongoDB connection established successfully.")

    try:
        DropoutPredictor().load_model()
    except Exception as e:
        logging.warning(f"No trained model found or error loading model: {str(e)}")


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


# API Endpoints
@app.post("/predict", response_model=PredictionOutput)
async def predict(student_data: StudentInput):
    logging.debug(f"Received request: {student_data.dict()}")
    try:
        return DropoutPredictor().predict(student_data)
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/predict", response_model=PredictionOutput)
async def predict(user_data: UserFriendlyInput):
    logging.debug(f"Received user-friendly request: {user_data.dict()}")
    try:
        # Transform user input to model-ready format
        model_input = transform_user_input(user_data)
        logging.debug(f"Transformed to model input: {model_input.dict()}")

        # Make prediction
        return DropoutPredictor().predict(model_input)
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files accepted")
    try:
        contents = await file.read()
        await upload_training_data(contents)
        return {"message": "Data uploaded successfully"}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await file.close()


async def ensure_db_connection():
    """Ensure database connection is established before performing operations"""
    global client, db

    # If already connected, return True
    if client is not None and db is not None:
        try:
            # Quick ping to check connection is still alive
            await db.command("ping")
            return True
        except Exception:
            # Connection was dropped, try to reconnect
            pass

    # Try to connect
    return await connect_to_mongo()


# Then modify your endpoint functions to use this:


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files accepted")

    # Ensure DB connection first
    if not await ensure_db_connection():
        raise HTTPException(503, "Database connection unavailable")

    try:
        contents = await file.read()
        await upload_training_data(contents)
        return {"message": "Data uploaded successfully"}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await file.close()


@app.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    try:
        # Ensure DB connection first
        if not await ensure_db_connection():
            raise HTTPException(503, "Database connection unavailable")

        # Check if there's new data to train on
        new_data = await get_new_training_data()

        # Safely check if new_data is None or empty
        if not new_data:
            return {
                "message": "No new data available for retraining",
                "status": "skipped",
            }

        # Set a flag in database that retraining is in progress
        try:
            await db["status"].update_one(
                {"_id": "retraining"},
                {
                    "$set": {
                        "status": "in_progress",
                        "started_at": datetime.datetime.utcnow(),
                        "data_points": len(new_data) if new_data else 0,
                    }
                },
                upsert=True,
            )
        except Exception as db_error:
            logging.error(f"Error updating retraining status: {str(db_error)}")
            # Continue anyway to try the retraining

        # Add the retraining task to background
        background_tasks.add_task(retrain_model)

        return {
            "message": "Retraining started in background",
            "status": "started",
            "data_points": len(new_data) if new_data else 0,
        }
    except Exception as e:
        logging.error(f"Failed to initiate retraining: {str(e)}")
        raise HTTPException(500, f"Failed to initiate retraining: {str(e)}")


# Helper functions
async def retrain_model():
    """Background task for model retraining"""
    try:
        # First check if db is available
        if not db:
            logging.error("Database not connected, cannot retrain")
            return

        # Get new training data
        new_data = await get_new_training_data()
        if not new_data:
            logging.info("No new data to train on")
            return

        # Set a flag in database that retraining is in progress
        await db["status"].update_one(
            {"_id": "retraining"},
            {
                "$set": {
                    "status": "in_progress",
                    "started_at": datetime.datetime.utcnow(),
                }
            },
            upsert=True,
        )

        df = pd.DataFrame(new_data)
        model = DropoutModel()

        # Log retraining details
        logging.info(f"Starting retraining with {len(df)} new data points")

        # Train the model and get metrics
        metrics = model.train(df)

        # Save training metrics to database
        await save_training_metrics(metrics)

        # Mark data as processed after successful training
        processed_count = await mark_data_as_processed(new_data)
        logging.info(
            f"Retraining completed successfully. Processed {processed_count} records."
        )

        # Update status to complete
        await db["status"].update_one(
            {"_id": "retraining"},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.datetime.utcnow(),
                    "last_metrics": metrics,
                }
            },
        )

        return metrics
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")

        # Make sure db is available before trying to update status
        if db is not None:
            try:
                await db["status"].update_one(
                    {"_id": "retraining"},
                    {
                        "$set": {
                            "status": "failed",
                            "error": str(e),
                            "failed_at": datetime.datetime.utcnow(),
                        }
                    },
                    upsert=True,
                )
            except Exception as db_error:
                # If updating the status fails, log that error too
                logging.error(f"Failed to update retraining status: {str(db_error)}")


@app.get("/retraining-status")
async def get_retraining_status():
    """Get the current status of model retraining"""
    try:
        # First check if the database connection is established
        if not db:
            return {"status": "not_started", "message": "Database not connected"}

        # Check if the collection exists
        collections = await db.list_collection_names()
        if "status" not in collections:
            return {"status": "not_started"}

        # Try to get the status document
        status_doc = await db["status"].find_one({"_id": "retraining"})
        if not status_doc:
            return {"status": "not_started"}

        # Convert ObjectId to string for JSON serialization
        if "_id" in status_doc and not isinstance(status_doc["_id"], str):
            status_doc["_id"] = str(status_doc["_id"])

        return status_doc
    except Exception as e:
        logging.error(f"Failed to get retraining status: {str(e)}")
        # Instead of raising an error, return a default status
        return {"status": "not_started", "error": str(e)}


@app.get("/training-metrics")
async def get_training_metrics():
    """Get the latest training metrics"""
    try:
        metrics = await get_latest_training_metrics()
        if not metrics:
            return {"message": "No training metrics available yet"}

        # Convert ObjectId to string for JSON serialization
        if "_id" in metrics:
            metrics["_id"] = str(metrics["_id"])

        return metrics
    except Exception as e:
        logging.error(f"Failed to get training metrics: {str(e)}")
        raise HTTPException(500, f"Failed to get training metrics: {str(e)}")


@app.get("/health/mongodb")
async def check_mongodb_connection():
    try:
        # Ping the database
        await db.command("ping")
        return {"status": "connected", "message": "Successfully connected to MongoDB"}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"MongoDB connection failed: {str(e)}"
        )
