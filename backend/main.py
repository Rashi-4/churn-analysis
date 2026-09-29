
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
from config import MODEL_PATH, ALLOWED_ORIGINS, API_HOST, API_PORT
from database import db
from explain_prediction import ChurnExplainer
import logging
from fastapi import UploadFile, File
import tempfile
import os

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

@app.onevent("startup")
async def startup_event():
    global model, explainer
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        logger.info("✓ Model loaded successfully")

        explainer = ChurnExplainer(MODEL_PATH)
        logger.info(" Explainer initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

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

@app.get("/", response_model=HealthResponse)
async def health_check():
    return {
        "status": "running",
        "model_loaded": model is not None,
        "explainer_loaded": explainer is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(customer: CustomerData):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        if explainer is None:
            raise HTTPException(status_code=500, detail="Explainer not loaded")

        customer_dict = customer.dict()
        
        explanation = explainer.explain_prediction(customer_dict)
        
        recommendation = explainer.get_recommendation(explanation['top_reasons'])

        prob = explanation['churn_probability']
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
            reasons=explanation['top_reasons'],
            recommendation=recommendation
        )

        logger.info(f"Prediction made for {customer_id}: {prob:.2%} churn")

        return {
            "churn_probability": prob,
            "prediction": explanation['prediction'],
            "top_reasons": explanation['top_reasons'],
            "recommendation": recommendation,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard-stats")
async def dashboard_stats():
    try:
        recent = db.get_recent_predictions(limit=5)
        
        if not recent:
            return {
                "total_predictions": 0,
                "avg_churn_probability": 0.0,
                "high_risk_count": 0,
                "recent_predictions": []
            }

        predictions = [r[2] for r in recent]  
        high_risk = len([p for p in predictions if p > 0.7])

        return {
            "total_predictions": len(recent),
            "avg_churn_probability": sum(predictions) / len(predictions),
            "high_risk_count": high_risk,
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
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions")
async def get_predictions(limit: int = 10):
    """Get recent predictions"""
    try:
        predictions = db.get_recent_predictions(limit=limit)
        return {
            "count": len(predictions),
            "predictions": [
                {
                    "id": p[0],
                    "customer_id": p[1],
                    "churn_probability": p[2],
                    "reasons": [p[3], p[4], p[5]],
                    "recommendation": p[6],
                    "created_at": p[7]
                }
                for p in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-info")
async def model_info():
    return {
        "model_type": "Gradient Boosting Classifier",
        "f1_score": 0.5945,
        "recall": 0.5508,
        "precision": 0.6458,
        "accuracy": 0.8006,
        "roc_auc": 0.8406,
        "features": 19,  
        "training_samples": 5634,
        "test_samples": 1409
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )