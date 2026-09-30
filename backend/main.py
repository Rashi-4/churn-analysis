from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
from pathlib import Path
from config import MODEL_PATH, ALLOWED_ORIGINS, API_HOST, API_PORT
from database import db
from explain_prediction import ChurnExplainer
import logging
import tempfile
import os
from fastapi.responses import FileResponse
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Churn Analysis API",
    description="Predict customer churn with explainable AI",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = None
explainer = None


@app.on_event("startup")
async def startup_event():
    global model, explainer

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        logger.info("✓ Model loaded successfully")

        explainer = ChurnExplainer(MODEL_PATH)

        logger.info("✓ Explainer initialized successfully")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================

class CustomerData(BaseModel):

    SeniorCitizen: int
    tenure: int
    MonthlyCharges: float
    TotalCharges: float

    gender_encoded: int
    Partner_encoded: int
    Dependents_encoded: int
    PhoneService_encoded: int
    MultipleLines_encoded: int
    InternetService_encoded: int
    OnlineSecurity_encoded: int
    OnlineBackup_encoded: int
    DeviceProtection_encoded: int
    TechSupport_encoded: int
    StreamingTV_encoded: int
    StreamingMovies_encoded: int
    Contract_encoded: int
    PaperlessBilling_encoded: int
    PaymentMethod_encoded: int


class PredictionResponse(BaseModel):

    churn_probability: float
    prediction: int
    top_reasons: List[dict]
    recommendation: str
    confidence: str


class HealthResponse(BaseModel):

    status: str
    model_loaded: bool
    explainer_loaded: bool


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/", response_model=HealthResponse)
async def health_check():

    return {
        "status": "running",
        "model_loaded": model is not None,
        "explainer_loaded": explainer is not None
    }


# =========================================================
# SINGLE CUSTOMER PREDICTION
# =========================================================

@app.post("/predict", response_model=PredictionResponse)
async def predict(customer: CustomerData):

    try:

        if model is None:
            raise HTTPException(
                status_code=500,
                detail="Model not loaded"
            )

        if explainer is None:
            raise HTTPException(
                status_code=500,
                detail="Explainer not loaded"
            )

        customer_dict = customer.dict()

        explanation = explainer.explain_prediction(
            customer_dict
        )

        recommendation = explainer.get_recommendation(
            explanation["top_reasons"]
        )

        prob = explanation["churn_probability"]

        if prob > 0.7:
            confidence = "high"

        elif prob > 0.4:
            confidence = "medium"

        else:
            confidence = "low"

        customer_id = f"CUST_{id(customer_dict)}"

        db.save_prediction(
            customer_id=customer_id,
            churn_prob=prob,
            reasons=explanation["top_reasons"],
            recommendation=recommendation
        )

        logger.info(
            f"Prediction made for {customer_id}: {prob:.2%} churn"
        )

        return {
            "churn_probability": prob,
            "prediction": explanation["prediction"],
            "top_reasons": explanation["top_reasons"],
            "recommendation": recommendation,
            "confidence": confidence
        }

    except Exception as e:

        logger.error(
            f"Prediction error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.get("/dashboard-stats")
async def dashboard_stats():

    try:

        recent = db.get_recent_predictions(
            limit=5
        )

        if not recent:

            return {
                "total_predictions": 0,
                "avg_churn_probability": 0.0,
                "high_risk_count": 0,
                "recent_predictions": []
            }

        predictions = [
            r[2]
            for r in recent
        ]

        high_risk = len([
            p for p in predictions
            if p > 0.7
        ])

        return {

            "total_predictions": len(recent),

            "avg_churn_probability":
                sum(predictions) / len(predictions),

            "high_risk_count":
                high_risk,

            "recent_predictions": [

                {
                    "customer_id": r[1],
                    "churn_probability": r[2],
                    "recommendation": r[6]
                }

                for r in recent
            ]
        }

    except Exception as e:

        logger.error(
            f"Stats error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# RECENT PREDICTIONS
# =========================================================

@app.get("/predictions")
async def get_predictions(limit: int = 10):

    try:

        predictions = db.get_recent_predictions(
            limit=limit
        )

        return {

            "count": len(predictions),

            "predictions": [

                {
                    "id": p[0],
                    "customer_id": p[1],
                    "churn_probability": p[2],
                    "reasons": [
                        p[3],
                        p[4],
                        p[5]
                    ],
                    "recommendation": p[6],
                    "created_at": p[7]
                }

                for p in predictions
            ]
        }

    except Exception as e:

        logger.error(
            f"Retrieval error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# RAW DATASET UPLOAD + BATCH PREDICTION
# =========================================================

@app.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...)
):

    tmp_path = None

    try:

        # -------------------------------------------------
        # Validate file
        # -------------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file uploaded"
            )

        if not file.filename.lower().endswith(".csv"):

            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV file"
            )

        # -------------------------------------------------
        # Save uploaded file temporarily
        # -------------------------------------------------

        contents = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as tmp:

            tmp.write(contents)
            tmp_path = tmp.name

        # -------------------------------------------------
        # Read CSV
        # -------------------------------------------------

        df = pd.read_csv(tmp_path)

        logger.info(
            f"Uploaded dataset shape: {df.shape}"
        )

        # -------------------------------------------------
        # Required RAW Telco columns
        # -------------------------------------------------

        required_columns = [

            "gender",
            "SeniorCitizen",
            "Partner",
            "Dependents",
            "tenure",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod",
            "MonthlyCharges",
            "TotalCharges"
        ]

        # -------------------------------------------------
        # Validate columns
        # -------------------------------------------------

        missing_columns = [

            column

            for column in required_columns

            if column not in df.columns

        ]

        if missing_columns:

            raise HTTPException(

                status_code=400,

                detail={

                    "message":
                        "Dataset is missing required Telco columns",

                    "missing_columns":
                        missing_columns,

                    "required_columns":
                        required_columns
                }
            )

        # -------------------------------------------------
        # Convert TotalCharges
        # -------------------------------------------------

        df["TotalCharges"] = pd.to_numeric(
            df["TotalCharges"],
            errors="coerce"
        )

        # -------------------------------------------------
        # Fill missing numeric values
        # -------------------------------------------------

        df["TotalCharges"] = df[
            "TotalCharges"
        ].fillna(
            df["TotalCharges"].median()
        )

        # -------------------------------------------------
        # Fill missing categorical values
        # -------------------------------------------------

        categorical_columns = [

            "gender",
            "Partner",
            "Dependents",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod"
        ]

        for column in categorical_columns:

            df[column] = df[column].fillna(
                df[column].mode()[0]
            )

        # -------------------------------------------------
        # Load saved encoders
        # -------------------------------------------------

        encoders_path = (
            Path("data") / "encoders.pkl"
        )

        if not encoders_path.exists():

            raise HTTPException(

                status_code=500,

                detail=
                    "Saved encoders not found. "
                    "Please run data preparation first."
            )

        with open(
            encoders_path,
            "rb"
        ) as f:

            encoders = pickle.load(f)

        # -------------------------------------------------
        # Encode categorical columns
        # -------------------------------------------------

        for column in categorical_columns:

            encoder = encoders[column]

            try:

                df[
                    column + "_encoded"
                ] = encoder.transform(
                    df[column].astype(str)
                )

            except ValueError as e:

                raise HTTPException(

                    status_code=400,

                    detail={
                        "message":
                            f"Unknown value found in column '{column}'.",

                        "column":
                            column,

                        "error":
                            str(e)
                    }
                )

        # -------------------------------------------------
        # Load exact feature order
        # -------------------------------------------------

        feature_names_path = (
            Path("data") / "feature_names.pkl"
        )

        if not feature_names_path.exists():

            raise HTTPException(

                status_code=500,

                detail=
                    "Feature names file not found. "
                    "Please run data preparation first."
            )

        with open(
            feature_names_path,
            "rb"
        ) as f:

            feature_names = pickle.load(f)

        # -------------------------------------------------
        # Prepare model input
        # -------------------------------------------------

        missing_features = [

            feature

            for feature in feature_names

            if feature not in df.columns

        ]

        if missing_features:

            raise HTTPException(

                status_code=400,

                detail={

                    "message":
                        "Could not create all model features",

                    "missing_features":
                        missing_features
                }
            )

        prediction_df = df[
            feature_names
        ].copy()

        logger.info(
            f"Prepared dataset shape: {prediction_df.shape}"
        )

        # -------------------------------------------------
        # Generate predictions
        # -------------------------------------------------

        predictions = []

        for index, row in prediction_df.iterrows():

            customer_dict = row.to_dict()

            explanation = (
                explainer.explain_prediction(
                    customer_dict
                )
            )

            recommendation = (
                explainer.get_recommendation(
                    explanation["top_reasons"]
                )
            )

            predictions.append({

                "row_number":
                    index + 1,

                "churn_probability":
                    explanation[
                        "churn_probability"
                    ],

                "prediction":
                    (
                        "Churn"
                        if explanation["prediction"] == 1
                        else "No Churn"
                    ),

                "top_reason":
                    (
                        explanation[
                            "top_reasons"
                        ][0]["plain_text"]

                        if explanation[
                            "top_reasons"
                        ]

                        else "Unknown"
                    ),

                "recommendation":
                    recommendation
            })

        # -------------------------------------------------
        # Risk classification
        # -------------------------------------------------

        high_risk_count = sum(

            1

            for prediction in predictions

            if prediction[
                "churn_probability"
            ] > 0.7
        )

        medium_risk_count = sum(

            1

            for prediction in predictions

            if 0.4 <
            prediction[
                "churn_probability"
            ] <= 0.7
        )

        low_risk_count = sum(

            1

            for prediction in predictions

            if prediction[
                "churn_probability"
            ] <= 0.4
        )

        # -------------------------------------------------
        # Save results
        # -------------------------------------------------

        results_df = pd.DataFrame(
            predictions
        )

        results_path = (
            "/tmp/churn_predictions.csv"
        )

        results_df.to_csv(
            results_path,
            index=False
        )

        # -------------------------------------------------
        # Return results
        # -------------------------------------------------

        return {

            "success": True,

            "total_rows":
                len(predictions),

            "high_risk_count":
                high_risk_count,

            "medium_risk_count":
                medium_risk_count,

            "low_risk_count":
                low_risk_count,

            # Show first 10 in frontend
            "predictions":
                predictions[:10]
        }

    except HTTPException:

        raise

    except Exception as e:

        logger.error(
            f"Dataset upload error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if (
            tmp_path
            and os.path.exists(tmp_path)
        ):

            os.unlink(tmp_path)


# =========================================================
# DOWNLOAD BATCH RESULTS
# =========================================================

@app.get("/download-results")
async def download_results():

    results_path = (
        "/tmp/churn_predictions.csv"
    )

    if not os.path.exists(
        results_path
    ):

        raise HTTPException(

            status_code=404,

            detail=
                "No prediction results available. "
                "Upload a dataset first."
        )

    return FileResponse(

        results_path,

        media_type="text/csv",

        filename="churn_predictions.csv"
    )


# =========================================================
# MODEL INFORMATION
# =========================================================

@app.get("/model-info")
async def model_info():

    return {

        "model_type":
            "Logistic Regression",

        "f1_score":
            0.5945,

        "recall":
            0.5508,

        "precision":
            0.6458,

        "accuracy":
            0.8006,

        "roc_auc":
            0.8406,

        "features":
            19,

        "training_samples":
            5634,

        "test_samples":
            1409
    }


# =========================================================
# GENERAL ERROR HANDLER
# =========================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request,
    exc
):

    logger.error(
        f"Unhandled exception: {exc}"
    )

    return {

        "error":
            "Internal server error",

        "detail":
            str(exc)
    }


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host=API_HOST,

        port=API_PORT,

        reload=False,

        log_level="info"
    )