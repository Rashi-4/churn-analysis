import React from 'react';
import './resultdisplay.css';

function prettifyFactor(factor) {
  return factor
    .replace('_encoded', '')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/_/g, ' ')
    .replace(/^./, (char) => char.toUpperCase());
}

function ResultDisplay({ prediction }) {
  const probability = prediction.churn_probability || 0;
  const percent = Math.round(probability * 100);
  const risk = percent > 70 ? 'HIGH RISK' : percent > 40 ? 'MEDIUM RISK' : 'LOW RISK';
  const riskClass = percent > 70 ? 'high' : percent > 40 ? 'medium' : 'low';

  return (
    <div className="result-display">
      <div className="result-head">
        <div>
          <span className="result-kicker">MODEL OUTPUT</span>
          <h3>Customer risk assessment</h3>
        </div>
        <span className={`risk-badge ${riskClass}`}>{risk}</span>
      </div>

      <div className="risk-overview">
        <div className="risk-ring" style={{ '--progress': `${percent}%` }}>
          <div className="risk-ring-inner">
            <strong>{percent}%</strong>
            <span>churn risk</span>
          </div>
        </div>
        <div className="risk-copy">
          <div className="risk-number">{prediction.prediction === 1 ? 'Churn predicted' : 'Retention predicted'}</div>
          <p>Model confidence: <strong>{prediction.confidence}</strong></p>
          <div className="probability-line"><span>0%</span><div><i style={{ width: `${percent}%` }} /></div><span>100%</span></div>
        </div>
      </div>

      <div className="result-section">
        <div className="section-label"><span>01</span> Why this prediction?</div>
        <div className="reason-list">
          {prediction.top_reasons.map((reason, index) => {
            const impact = Number(reason.impact || 0);
            const width = Math.min(100, Math.max(12, Number(reason.impact_percentage || 0)));
            return (
              <div className="reason" key={`${reason.factor}-${index}`}>
                <div className={`reason-marker ${impact > 0 ? 'positive' : 'negative'}`}>{impact > 0 ? '↑' : '↓'}</div>
                <div className="reason-main">
                  <div className="reason-title"><strong>{prettifyFactor(reason.factor)}</strong><span>{impact > 0 ? 'Raises risk' : 'Reduces risk'}</span></div>
                  <p>{reason.plain_text}</p>
                  <div className="reason-track"><i className={impact > 0 ? 'positive' : 'negative'} style={{ width: `${width}%` }} /></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="action-card">
        <div className="action-icon">✦</div>
        <div>
          <span className="action-kicker">RECOMMENDED RETENTION ACTION</span>
          <h4>What should the business do next?</h4>
          <p>{prediction.recommendation}</p>
        </div>
      </div>

      <div className="explain-note">
        <span>SHAP</span>
        <p>Feature contributions are shown for this individual prediction, so the result is explainable rather than just a probability score.</p>
      </div>
    </div>
  );
}

export default ResultDisplay;
