
# Configuration settings for backend

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

DATASET_PATH = DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
TRAIN_DATA_PATH = DATA_DIR / "train_data.csv"
TEST_DATA_PATH = DATA_DIR / "test_data.csv"

MODEL_PATH = MODEL_DIR / "churn_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.pkl"

DATABASE_URL = BASE_DIR / "churn_predictions.db"

API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

TEST_SIZE = 0.2
RANDOM_STATE = 42
MODEL_TYPE = "gradient_boosting"  

CATEGORICAL_FEATURES = ['Contract', 'InternetService', 'PaymentMethod']
NUMERICAL_FEATURES = ['Tenure', 'MonthlyCharges', 'TotalCharges']

print(f"Config loaded. Dataset path: {DATASET_PATH}")