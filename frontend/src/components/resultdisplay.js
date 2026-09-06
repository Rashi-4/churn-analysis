import React from 'react';
import './ResultDisplay.css';

function ResultDisplay({ prediction }) {
  const getRiskColor = (probability) => {
    if (probability > 0.7) return '#f44336';
    if (probability > 0.4) return '#ff9800';
    return '#4caf50';
  };

  const getRiskLevel = (probability) => {
    if (probability > 0.7) return 'HIGH RISK';
    if (probability > 0.4) return 'MEDIUM RISK';
    return 'LOW RISK';
  };

  const riskColor = getRiskColor(prediction.churn_probability);
  const riskLevel = getRiskLevel(prediction.churn_probability);

  return (
    <div className="result-display">
      <h2>🔍 Prediction Results</h2>

      <div className="probability-card" style={{ borderLeftColor: riskColor }}>
        <div className="probability-circle" style={{ borderColor: riskColor }}>
          <div className="probability-value">
            {(prediction.churn_probability * 100).toFixed(0)}%
          </div>
        </div>
        <div className="probability-info">
          <p className="risk-level" style={{ color: riskColor }}>
            {riskLevel}
          </p>
          <p className="confidence">
            Confidence: {prediction.confidence.toUpperCase()}
          </p>
        </div>
      </div>

      <div className="reasons-section">
        <h3>📊 Top Risk Factors</h3>
        <div className="reasons-list">
          {prediction.top_reasons.map((reason, index) => (
            <div key={index} className="reason-item">
              <div className="reason-number">{index + 1}</div>
              <div className="reason-content">
                <p className="reason-text">{reason.plain_text}</p>
                <div className="reason-bar">
                  <div
                    className="reason-bar-fill"
                    style={{
                      width: `${reason.impact_percentage}%`,
                      backgroundColor: reason.impact > 0 ? '#f44336' : '#4caf50',
                    }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recommendation-section">
        <h3>💡 Recommended Action</h3>
        <div className="recommendation-card">
          <p>{prediction.recommendation}</p>
        </div>
      </div>
    </div>
  );
}

export default ResultDisplay;