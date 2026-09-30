# ChurnGuard AI

An end-to-end **customer churn prediction and explainability system** built with machine learning, FastAPI, React, SHAP, and SQLite.

The project predicts customer churn probability, identifies the factors influencing predictions, and provides rule-based retention recommendations. It supports both **individual customer prediction** and **batch analysis of raw customer datasets**.

## Features

* **Single Customer Prediction** — predict churn probability from customer details.
* **Explainable AI** — SHAP-based identification of important prediction factors.
* **Risk Classification** — High, Medium, and Low churn-risk categories.
* **Batch Dataset Analysis** — upload the raw Telco Customer Churn CSV and analyze multiple customers.
* **Retention Recommendations** — rule-based suggestions based on influential factors.
* **React Dashboard** — view prediction statistics and recent results.
* **REST API** — FastAPI endpoints for prediction and dataset analysis.
* **SQLite Storage** — stores prediction records and recommendations.
* **Downloadable Results** — export batch predictions as CSV.

## Workflow

```text
Raw Customer Data
       ↓
Data Preprocessing
       ↓
Feature Encoding
       ↓
ML Model
       ↓
Churn Probability
       ↓
SHAP Explanation
       ↓
Risk Classification
       ↓
Retention Recommendation
       ↓
FastAPI Backend
       ↓
React Dashboard
```

## Machine Learning

Three models were evaluated:

* Logistic Regression
* Random Forest
* Gradient Boosting

### Model Performance

| Model               | Accuracy | Precision | Recall |         F1 |    ROC-AUC |
| ------------------- | -------: | --------: | -----: | ---------: | ---------: |
| Logistic Regression |   80.06% |    64.58% | 55.08% | **59.45%** |     84.06% |
| Random Forest       |   79.77% |    65.19% | 51.07% |     57.27% | **84.17%** |
| Gradient Boosting   |   79.49% |    64.31% | 51.07% |     56.93% |     83.36% |

**Selected model: Logistic Regression**, based on the highest F1-score among the evaluated models.

The model achieved:

* **Accuracy:** 80.06%
* **Precision:** 64.58%
* **Recall:** 55.08%
* **F1-score:** 59.45%
* **ROC-AUC:** 84.06%

## Batch Analysis

The system accepts the original Telco Customer Churn CSV and performs preprocessing and prediction automatically.

The complete dataset of **7,043 customers** was successfully processed.

```text
Total Customers : 7043
High Risk       : 430
Medium Risk     : 1664
Low Risk        : 4949
```

## Explainability

SHAP is used to identify the features contributing to individual predictions.

Examples of influential features include:

* Tenure
* Monthly Charges
* Contract
* Internet Service
* Online Security
* Payment Method

SHAP values are treated as model contributions rather than percentage changes or causal effects.

## Tech Stack

**Machine Learning**

* Python
* Pandas
* NumPy
* Scikit-learn
* SHAP

**Backend**

* FastAPI
* Uvicorn
* Pydantic
* SQLite

**Frontend**

* React
* JavaScript
* HTML
* CSS

**Tools**

* Git
* GitHub
* VS Code
* Jupyter Notebook

## Project Structure

```text
ChurnAnalysis/
├── backend/
│   ├── config.py
│   ├── data_preparation.py
│   ├── database.py
│   ├── explain_prediction.py
│   ├── main.py
│   └── train_model.py
│
├── data/
│   ├── encoders.pkl
│   └── feature_names.pkl
│
├── models/
│   └── churn_model.pkl
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── app.js
│       └── app.css
│
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

## My Contribution — Rashi Arora

**Team Lead & Backend Developer**

* Designed and implemented the FastAPI backend
* Developed prediction and batch-analysis APIs
* Integrated the ML model with the backend
* Integrated SHAP explainability
* Implemented raw CSV preprocessing for batch inference
* Implemented SQLite prediction storage
* Added backend validation, logging, and error handling
* Integrated frontend and backend components
* Coordinated integration across the team

## Team

| Member              | Role                                |
| ------------------- | ----------------------------------- |
| **Rashi Arora**     | Team Lead & Backend Developer       |
| **Shashwat Tiwari** | Frontend Developer 
| **Radhika Gupta**   | ML Developer and Explainability                       |
| **Samia Khan**      | Data Analyst                        |
| **Prakash Dixit**   | Frontend Developer                  |

## Run Locally

### Backend

```bash
git clone git@github.com:Rashi-4/churn-analysis.git
cd churn-analysis

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python backend/main.py
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Project Status

**Functional Academic Project**

The current implementation covers the complete workflow from customer data preprocessing and model inference to SHAP explainability, REST APIs, React visualization, database storage, and batch analysis.

## Repository

[GitHub Repository](https://github.com/Rashi-4/churn-analysis)

## Disclaimer

This project is intended for educational and demonstration purposes. Churn predictions and retention recommendations should be treated as model outputs rather than definitive business decisions.
