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
    db,
)
from app.schema import StudentInput, PredictionOutput, UserFriendlyInput
from app.scripts.model import DropoutModel
import pandas as pd
import logging
from app.config import settings

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
    await connect_to_mongo()
    try:
        DropoutPredictor().load_model()
    except:
        logging.warning("No trained model found")


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


@app.post("/retrain")
async def retrain(background_tasks: BackgroundTasks):
    try:
        # Check if there's new data to train on
        new_data = await get_new_training_data()
        if not new_data:
            return {
                "message": "No new data available for retraining",
                "status": "skipped",
            }

        # Add the retraining task to background
        background_tasks.add_task(retrain_model)
        return {"message": "Retraining started in background", "status": "started"}
    except Exception as e:
        logging.error(f"Failed to initiate retraining: {str(e)}")
        raise HTTPException(500, f"Failed to initiate retraining: {str(e)}")


# Helper functions
async def retrain_model():
    try:
        new_data = await get_new_training_data()
        if not new_data:
            logging.info("No new data to train on")
            return

        df = pd.DataFrame(new_data)
        model = DropoutModel()

        # Log retraining details
        logging.info(f"Starting retraining with {len(df)} new data points")

        # Train the model
        model.train(df)

        # Mark data as processed after successful training
        processed_count = await mark_data_as_processed(new_data)
        logging.info(
            f"Retraining completed successfully. Processed {processed_count} records."
        )
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")


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
