# Setup Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 14 or higher
- Git
- GitHub account
- Kaggle account (for dataset)

## Step-by-Step Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/churn-analysis.git
cd churn-analysis
```

### 2. Create Python Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import pandas, sklearn, shap, fastapi; print('All packages installed!')"
```

### 4. Download Dataset

1. Go to [Kaggle Telco Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
2. Download `WA_Fn-UseC_-Telco-Customer-Churn.csv`
3. Move to `data/` folder
4. File should be: `data/WA_Fn-UseC_-Telco-Customer-Churn.csv`

### 5. Prepare Data & Train Model

```bash
cd backend
python data_preparation.py
python train_model.py
```

This will:
- Load and clean data
- Split into train/test
- Train ML models
- Save best model to `models/churn_model.pkl`

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 7. Run Backend Server

Terminal Window 1:
```bash
cd backend
python main.py
```

You should see: