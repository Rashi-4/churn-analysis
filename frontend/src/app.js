import React, { useEffect, useState } from 'react';
import './app.css';
import PredictionForm from './components/predictionform';
import ResultDisplay from './components/resultdisplay';

const API = 'http://localhost:8000';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [healthRes, modelRes, statsRes] = await Promise.all([
        fetch(`${API}/`),
        fetch(`${API}/model-info`),
        fetch(`${API}/dashboard-stats`),
      ]);

      if (healthRes.ok) {
        const health = await healthRes.json();
        setApiOnline(health.status === 'running' && health.model_loaded);
      }
      if (modelRes.ok) setModelInfo(await modelRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (err) {
      setApiOnline(false);
      console.error('Dashboard API unavailable', err);
    }
  };

  const handlePredict = async (customerData) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerData),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `API error: ${response.status}`);
      }

      setPrediction(data);
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Failed to get prediction');
    } finally {
      setLoading(false);
    }
  };

  const recentCount = stats?.total_predictions ?? 0;
  const highRisk = stats?.high_risk_count ?? 0;
  const avgRisk = stats ? Math.round((stats.avg_churn_probability || 0) * 100) : 0;

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">CA</div>
          <div>
            <div className="brand-name">CHURN<span>AI</span></div>
            <div className="brand-subtitle">Explainable Customer Retention</div>
          </div>
        </div>

        <div className="topbar-meta">
          <div className="model-pill">
            <span className="pulse-dot" />
            {apiOnline ? 'API ONLINE' : 'API OFFLINE'}
          </div>
          <div className="model-label">
            Model: <strong>{modelInfo?.model_type || 'Gradient Boosting'}</strong>
          </div>
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <p className="eyebrow">CUSTOMER RETENTION INTELLIGENCE</p>
            <h1>Predict. Explain. <span>Retain.</span></h1>
            <p className="hero-copy">
              Identify customers at risk of churn, understand the factors behind each prediction,
              and turn model insights into a practical retention action.
            </p>
          </div>
          <div className="hero-badge">
            <div className="hero-badge-icon">✦</div>
            <div>
              <strong>Explainable AI</strong>
              <small>SHAP-powered insights</small>
            </div>
          </div>
        </section>

        <section className="metrics-grid">
          <MetricCard icon="◉" label="Recent Predictions" value={recentCount} hint="Saved by the backend" />
          <MetricCard icon="!" label="High-Risk Cases" value={highRisk} hint="Probability above 70%" accent="danger" />
          <MetricCard icon="↗" label="Average Churn Risk" value={`${avgRisk}%`} hint="Across recent predictions" accent="warning" />
          <MetricCard icon="F1" label="Model F1 Score" value={modelInfo ? modelInfo.f1_score.toFixed(2) : '—'} hint="Held-out test set" accent="violet" />
        </section>

        <section className="workspace">
          <div className="section-heading">
            <div>
              <p className="eyebrow">LIVE ANALYSIS</p>
              <h2>Analyze a customer</h2>
            </div>
            <div className="flow-indicator">
              <span>01 Input</span><i>→</i><span>02 ML</span><i>→</i><span>03 SHAP</span><i>→</i><span>04 Action</span>
            </div>
          </div>

          <div className="analysis-grid">
            <PredictionForm onPredict={handlePredict} loading={loading} />

            <div className="result-area">
              {error && (
                <div className="error-panel">
                  <strong>Prediction failed</strong>
                  <span>{error}</span>
                </div>
              )}

              {loading && (
                <div className="empty-panel loading-panel">
                  <div className="loader-ring" />
                  <p>Running the customer through the model…</p>
                  <small>Calculating churn probability and SHAP factors</small>
                </div>
              )}

              {!loading && !prediction && !error && (
                <div className="empty-panel">
                  <div className="empty-icon">✦</div>
                  <h3>Your prediction appears here</h3>
                  <p>Enter the customer profile and click <strong>Analyze Customer</strong>.</p>
                  <div className="empty-flow">
                    <span>Customer data</span><b>→</b><span>Gradient Boosting</span><b>→</b><span>SHAP</span>
                  </div>
                </div>
              )}

              {!loading && prediction && <ResultDisplay prediction={prediction} />}
            </div>
          </div>
        </section>

        <section className="explain-strip">
          <div className="explain-item">
            <div className="explain-icon">01</div>
            <div><strong>Prediction</strong><p>Gradient Boosting estimates the probability that the customer will churn.</p></div>
          </div>
          <div className="explain-item">
            <div className="explain-icon">02</div>
            <div><strong>Explanation</strong><p>SHAP identifies the features that contributed most to this individual prediction.</p></div>
          </div>
          <div className="explain-item">
            <div className="explain-icon">03</div>
            <div><strong>Retention</strong><p>Business rules convert the strongest risk factor into a suggested next action.</p></div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <span>CHURN ANALYSIS</span>
        <span>PSIT • CS-AIML • 2026</span>
        <span>React + FastAPI + Scikit-learn + SHAP</span>
      </footer>
    </div>
  );
}

function MetricCard({ icon, label, value, hint, accent = '' }) {
  return (
    <div className={`metric-card ${accent}`}>
      <div className="metric-top"><span className="metric-icon">{icon}</span><span>{label}</span></div>
      <div className="metric-value">{value}</div>
      <div className="metric-hint">{hint}</div>
    </div>
  );
}

export default App;
