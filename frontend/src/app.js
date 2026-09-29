import React, { useState } from 'react';
import PredictionForm from './components/predictionform';
import ResultDisplay from './components/resultdisplay';
import DatasetUpload from './components/datasetupload';
import Dashboard from './components/dashboard';
import './app.css';

function App() {
  const [activeTab, setActiveTab] = useState('single');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (customerData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Prediction failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setActiveTab('dashboard');
  };

  return (
    <div className="app">

      <header className="app-header">
        <div className="header-content">
          <div className="brand-icon">AI</div>

          <div>
            <h1>ChurnGuard AI</h1>
            <p>Explainable Customer Churn Prediction</p>
          </div>
        </div>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'single' ? 'active' : ''}
          onClick={() => setActiveTab('single')}
        >
          Single Prediction
        </button>

        <button
          className={activeTab === 'upload' ? 'active' : ''}
          onClick={() => setActiveTab('upload')}
        >
          Dataset Analysis
        </button>

        <button
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
      </nav>

      <main className="main-content">

        {activeTab === 'single' && (
          <>
            <section className="page-intro">
              <span className="eyebrow">PREDICT & EXPLAIN</span>
              <h2>Analyze Customer Churn Risk</h2>
              <p>
                Enter customer information to predict churn probability
                and understand the factors influencing the prediction.
              </p>
            </section>

            <div className="single-layout">
              <PredictionForm
                onPredict={handlePredict}
                loading={loading}
              />

              <div>
                {error && (
                  <div className="error-message">
                    <strong>Prediction Error</strong>
                    <p>{error}</p>
                  </div>
                )}

                {loading && (
                  <div className="loading-card">
                    <div className="spinner"></div>
                    <h3>Analyzing customer...</h3>
                    <p>Running the ML model and SHAP explanation.</p>
                  </div>
                )}

                {result && !loading && (
                  <ResultDisplay result={result} />
                )}

                {!result && !loading && !error && (
                  <div className="empty-result">
                    <div className="empty-icon">✦</div>
                    <h3>Prediction results will appear here</h3>
                    <p>
                      Submit the customer information to see churn
                      probability, SHAP-based reasons and a retention
                      recommendation.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {activeTab === 'upload' && (
          <>
            <section className="page-intro">
              <span className="eyebrow">BATCH ANALYSIS</span>
              <h2>Analyze Your Customer Dataset</h2>
              <p>
                Upload a compatible CSV dataset and generate churn
                predictions for multiple customers.
              </p>
            </section>

            <DatasetUpload onUploadSuccess={handleUploadSuccess} />
          </>
        )}

        {activeTab === 'dashboard' && (
          <>
            <section className="page-intro">
              <span className="eyebrow">OVERVIEW</span>
              <h2>Prediction Dashboard</h2>
              <p>
                View recent predictions and overall churn-risk statistics.
              </p>
            </section>

            <Dashboard />
          </>
        )}

      </main>

      <footer className="app-footer">
        <p>
          ChurnGuard AI • Logistic Regression • SHAP Explainability
        </p>
      </footer>

    </div>
  );
}

export default App;