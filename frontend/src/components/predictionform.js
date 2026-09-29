import React, { useState } from 'react';
import './predictionform.css';

const initialData = {
  SeniorCitizen: 0,
  tenure: 12,
  MonthlyCharges: 65.5,
  TotalCharges: 786,
  gender_encoded: 1,
  Partner_encoded: 0,
  Dependents_encoded: 0,
  PhoneService_encoded: 1,
  MultipleLines_encoded: 0,
  InternetService_encoded: 1,
  OnlineSecurity_encoded: 0,
  OnlineBackup_encoded: 0,
  DeviceProtection_encoded: 0,
  TechSupport_encoded: 0,
  StreamingTV_encoded: 1,
  StreamingMovies_encoded: 1,
  Contract_encoded: 0,
  PaperlessBilling_encoded: 1,
  PaymentMethod_encoded: 2,
};

function PredictionForm({ onPredict, loading }) {
  const [formData, setFormData] = useState(initialData);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((current) => ({
      ...current,
      [name]: type === 'number' ? Number(value) : Number(value),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  const resetForm = () => setFormData(initialData);

  return (
    <form className="prediction-form" onSubmit={handleSubmit}>
      <div className="form-head">
        <div>
          <span className="form-kicker">CUSTOMER PROFILE</span>
          <h3>Enter customer data</h3>
          <p>These fields are converted to the 19 features expected by the trained model.</p>
        </div>
        <button type="button" className="reset-btn" onClick={resetForm}>Reset</button>
      </div>

      <div className="form-section">
        <div className="form-section-title"><span>01</span> Billing & tenure</div>
        <div className="field-grid two">
          <NumberField label="Tenure (months)" name="tenure" value={formData.tenure} min="0" max="72" onChange={handleChange} />
          <NumberField label="Monthly charges ($)" name="MonthlyCharges" value={formData.MonthlyCharges} min="0" max="200" step="0.01" onChange={handleChange} />
          <NumberField label="Total charges ($)" name="TotalCharges" value={formData.TotalCharges} min="0" max="10000" step="0.01" onChange={handleChange} />
          <SelectField label="Contract" name="Contract_encoded" value={formData.Contract_encoded} onChange={handleChange} options={['Month-to-month', 'One year', 'Two year']} />
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title"><span>02</span> Customer profile</div>
        <div className="field-grid two">
          <SelectField label="Gender" name="gender_encoded" value={formData.gender_encoded} onChange={handleChange} options={['Female', 'Male']} />
          <SelectField label="Senior citizen" name="SeniorCitizen" value={formData.SeniorCitizen} onChange={handleChange} options={['No', 'Yes']} />
          <SelectField label="Partner" name="Partner_encoded" value={formData.Partner_encoded} onChange={handleChange} options={['No', 'Yes']} />
          <SelectField label="Dependents" name="Dependents_encoded" value={formData.Dependents_encoded} onChange={handleChange} options={['No', 'Yes']} />
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title"><span>03</span> Services</div>
        <div className="field-grid two">
          <SelectField label="Phone service" name="PhoneService_encoded" value={formData.PhoneService_encoded} onChange={handleChange} options={['No', 'Yes']} />
          <SelectField label="Multiple lines" name="MultipleLines_encoded" value={formData.MultipleLines_encoded} onChange={handleChange} options={['No', 'No phone service', 'Yes']} />
          <SelectField label="Internet service" name="InternetService_encoded" value={formData.InternetService_encoded} onChange={handleChange} options={['DSL', 'Fiber optic', 'No']} />
          <SelectField label="Online security" name="OnlineSecurity_encoded" value={formData.OnlineSecurity_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
          <SelectField label="Online backup" name="OnlineBackup_encoded" value={formData.OnlineBackup_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
          <SelectField label="Device protection" name="DeviceProtection_encoded" value={formData.DeviceProtection_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
          <SelectField label="Tech support" name="TechSupport_encoded" value={formData.TechSupport_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
          <SelectField label="Streaming TV" name="StreamingTV_encoded" value={formData.StreamingTV_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
          <SelectField label="Streaming movies" name="StreamingMovies_encoded" value={formData.StreamingMovies_encoded} onChange={handleChange} options={['No', 'No internet service', 'Yes']} />
        </div>
      </div>

      <div className="form-section last">
        <div className="form-section-title"><span>04</span> Billing preferences</div>
        <div className="field-grid two">
          <SelectField label="Paperless billing" name="PaperlessBilling_encoded" value={formData.PaperlessBilling_encoded} onChange={handleChange} options={['No', 'Yes']} />
          <SelectField label="Payment method" name="PaymentMethod_encoded" value={formData.PaymentMethod_encoded} onChange={handleChange} options={['Bank transfer (automatic)', 'Credit card (automatic)', 'Electronic check', 'Mailed check']} />
        </div>
      </div>

      <button className="analyze-btn" type="submit" disabled={loading}>
        <span>{loading ? 'Analyzing customer…' : 'Analyze Customer'}</span>
        <span className="button-arrow">→</span>
      </button>
    </form>
  );
}

function NumberField({ label, ...props }) {
  return <label className="field"><span>{label}</span><input type="number" {...props} required /></label>;
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select name={name} value={value} onChange={onChange}>
        {options.map((option, index) => <option key={option} value={index}>{option}</option>)}
      </select>
    </label>
  );
}

export default PredictionForm;
