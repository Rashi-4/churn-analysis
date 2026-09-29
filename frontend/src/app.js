import React, { useState, useEffect } from 'react';
import './app.css';
import PredictionForm from './components/predictionform';
import ResultDisplay from './components/resultdisplay';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/');
      if (response.ok) {
        const data = await response.json();
        setApiStatus(data.status);
      }
    } catch (err) {
      setApiStatus('offline');
      console.error('API unreachable');
    }
  };

  const handlePredict = async (customerData) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerData), //converts javascript object to JSON string
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message || 'Failed to get prediction');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Churn Analysis Dashboard</h1>
        <p>Predict customer churn and get actionable retention strategies</p>
        <div className={`status ${apiStatus}`}>
          API Status: {apiStatus === 'running' ? '🟢 Online' : '🔴 Offline'}
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <PredictionForm onPredict={handlePredict} loading={loading} />

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Getting prediction...</p>
            </div>
          )}

          {prediction && !loading && (
            <ResultDisplay prediction={prediction} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2026 Churn Analysis Team | PSIT, Kanpur</p>
      </footer>
    </div>
  );
}

export default App;