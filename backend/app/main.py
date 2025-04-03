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
    get_retraining_status,
    update_retraining_status,
    is_connected,
)
from app.schema import StudentInput, PredictionOutput, UserFriendlyInput
from app.scripts.model import DropoutModel
import pandas as pd
import logging
from app.config import settings
import datetime

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Student Dropout Prediction API",
    description="API for predicting and managing student dropout risk",
    version="1.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENABLE_CORS else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
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
        logging.info("Model loaded successfully.")
    except Exception as e:
        logging.warning(f"No trained model found or error loading model: {str(e)}")


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()
    logging.info("Application shutdown: MongoDB connection closed.")


# Helper function to check database connection
async def ensure_db_connection():
    """Ensure database connection is established"""
    if not await is_connected():
        connected = await connect_to_mongo()
        if not connected:
            raise HTTPException(503, "Database connection unavailable")
        return connected
    return True


# API Endpoints
@app.post("/predict", response_model=PredictionOutput)
async def predict_raw(student_data: StudentInput):
    """Raw prediction endpoint that accepts model-ready input format."""
    # Ensure database connection
    await ensure_db_connection()

    logging.debug(f"Received raw prediction request: {student_data.dict()}")
    try:
        return DropoutPredictor().predict(student_data)
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(400, str(e))


@app.post("/predict/user", response_model=PredictionOutput)
async def predict_user_friendly(user_data: UserFriendlyInput):
    """User-friendly prediction endpoint with more intuitive input format."""
    # Ensure database connection
    await ensure_db_connection()

    logging.debug(f"Received user-friendly request: {user_data.dict()}")
    try:
        # Transform user input to model-ready format
        model_input = transform_user_input(user_data)
        logging.debug(f"Transformed to model input: {model_input.dict()}")

        # Make prediction
        return DropoutPredictor().predict(model_input)
    except Exception as e:
        logging.error(f"User-friendly prediction error: {str(e)}")
        raise HTTPException(400, str(e))


@app.post("/upload-data")
async def upload_data(
    file: UploadFile = File(...),
):
    """Upload CSV training data."""
    # Ensure database connection
    await ensure_db_connection()

    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files accepted")

    try:
        contents = await file.read()
        records_count = await upload_training_data(contents)
        return {"message": "Data uploaded successfully", "records": records_count}
    except ValueError as e:
        # This is likely a validation error with the CSV
        raise HTTPException(400, str(e))
    except Exception as e:
        logging.error(f"File upload error: {str(e)}")
        raise HTTPException(500, str(e))
    finally:
        await file.close()


@app.post("/retrain")
async def retrain(
    background_tasks: BackgroundTasks,
):
    """Initiate model retraining process."""
    # Ensure database connection
    await ensure_db_connection()

    try:
        # Check if there's new data to train on
        new_data = await get_new_training_data()

        # Safely check if new_data is None or empty
        if not new_data:
            return {
                "message": "No new data available for retraining",
                "status": "skipped",
            }

        # Update retraining status to in_progress
        await update_retraining_status("in_progress", {"data_points": len(new_data)})

        # Add the retraining task to background
        background_tasks.add_task(retrain_model_task)

        return {
            "message": "Retraining started in background",
            "status": "started",
            "data_points": len(new_data),
        }
    except Exception as e:
        logging.error(f"Failed to initiate retraining: {str(e)}")
        # Update status to failed
        await update_retraining_status("failed", {"error": str(e)})
        raise HTTPException(500, f"Failed to initiate retraining: {str(e)}")


# Helper functions
async def retrain_model_task():
    """Background task for model retraining."""
    try:
        # Ensure DB connection
        if not await is_connected():
            if not await connect_to_mongo():
                logging.error("Database not connected, cannot retrain")
                await update_retraining_status(
                    "failed", {"error": "Database connection lost"}
                )
                return

        # Get new training data
        new_data = await get_new_training_data()
        if not new_data:
            logging.info("No new data to train on")
            await update_retraining_status(
                "completed", {"message": "No new data to train on"}
            )
            return

        # Update status to show retraining in progress
        data_points = len(new_data)
        await update_retraining_status(
            "in_progress",
            {
                "data_points": data_points,
                "message": f"Training on {data_points} new records",
            },
        )

        # Convert to DataFrame for training
        df = pd.DataFrame(new_data)
        model = DropoutModel()

        # Log retraining details
        logging.info(f"Starting retraining with {len(df)} new data points")

        # Train the model and get metrics
        metrics = model.train(df)

        # Add data size to metrics
        metrics["data_points"] = data_points

        # Save training metrics to database
        await save_training_metrics(metrics)

        # Mark data as processed after successful training
        processed_count = await mark_data_as_processed(new_data)
        logging.info(
            f"Retraining completed successfully. Processed {processed_count} records."
        )

        # Update status to complete
        await update_retraining_status(
            "completed", {"last_metrics": metrics, "processed_records": processed_count}
        )

        return metrics
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")

        # Update status to failed
        await update_retraining_status(
            "failed",
            {
                "error": str(e),
            },
        )

        return {"error": str(e)}


@app.get("/retraining-status")
async def get_retraining_info():
    """Get the current status of model retraining."""
    # Ensure database connection
    await ensure_db_connection()

    try:
        status_doc = await get_retraining_status()
        return status_doc
    except Exception as e:
        logging.error(f"Failed to get retraining status: {str(e)}")
        raise HTTPException(500, f"Failed to get retraining status: {str(e)}")


@app.get("/training-metrics")
async def get_training_info():
    """Get the latest training metrics."""
    # Ensure database connection
    await ensure_db_connection()

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


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.get("/health/mongodb")
async def check_mongodb_connection():
    """Check MongoDB connection health."""
    try:
        if await is_connected():
            return {
                "status": "connected",
                "message": "Successfully connected to MongoDB",
            }
        # Try to reconnect
        if await connect_to_mongo():
            return {
                "status": "connected",
                "message": "Successfully reconnected to MongoDB",
            }
        raise HTTPException(status_code=503, detail="MongoDB connection unavailable")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"MongoDB connection failed: {str(e)}"
        )
