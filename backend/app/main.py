from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .scripts.prediction import DropoutPredictor
from .db import (
    connect_to_mongo,
    close_mongo_connection,
    upload_training_data,
    get_new_training_data,
    mark_data_as_processed,
)
from app.schema import StudentInput, PredictionOutput
from app.scripts.model import DropoutModel
import pandas as pd
import io
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
    try:
        return DropoutPredictor().predict(student_data)
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
    background_tasks.add_task(retrain_model)
    return {"message": "Retraining started in background"}


# Helper functions
async def retrain_model():
    try:
        new_data = await get_new_training_data()
        if not new_data:
            return

        df = pd.DataFrame(new_data)
        model = DropoutModel()
        model.train(df)
        await mark_data_as_processed(new_data)
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")
