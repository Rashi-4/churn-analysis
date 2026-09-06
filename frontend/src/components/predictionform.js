import React, { useState } from 'react';
import './PredictionForm.css';

function PredictionForm({ onPredict, loading }) {
  const [formData, setFormData] = useState({
    Tenure: 12,
    MonthlyCharges: 65.5,
    TotalCharges: 786,
    InternetService_encoded: 1,
    Contract_encoded: 1,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'Tenure' ? parseInt(value) : parseFloat(value),
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  return (
    <div className="prediction-form">
      <h2>📝 Customer Information</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="Tenure">Tenure (months)</label>
          <input
            type="number"
            id="Tenure"
            name="Tenure"
            value={formData.Tenure}
            onChange={handleChange}
            min="0"
            max="72"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="MonthlyCharges">Monthly Charges ($)</label>
          <input
            type="number"
            id="MonthlyCharges"
            name="MonthlyCharges"
            value={formData.MonthlyCharges}
            onChange={handleChange}
            min="0"
            max="200"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="TotalCharges">Total Charges ($)</label>
          <input
            type="number"
            id="TotalCharges"
            name="TotalCharges"
            value={formData.TotalCharges}
            onChange={handleChange}
            min="0"
            max="10000"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="InternetService_encoded">Internet Service Type</label>
          <select
            id="InternetService_encoded"
            name="InternetService_encoded"
            value={formData.InternetService_encoded}
            onChange={handleChange}
          >
            <option value={0}>DSL</option>
            <option value={1}>Fiber Optic</option>
            <option value={2}>No Service</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="Contract_encoded">Contract Type</label>
          <select
            id="Contract_encoded"
            name="Contract_encoded"
            value={formData.Contract_encoded}
            onChange={handleChange}
          >
            <option value={0}>Month-to-Month</option>
            <option value={1}>One Year</option>
            <option value={2}>Two Year</option>
          </select>
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Analyzing...' : 'Get Prediction'}
        </button>
      </form>
    </div>
  );
}

export default PredictionForm;