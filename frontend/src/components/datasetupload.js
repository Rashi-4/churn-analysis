import React, { useState } from 'react';
import './datasetupload.css';

function DatasetUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResults(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/upload-dataset',
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || 'Upload failed');
      }

      setResults(data);

      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">

      <div className="upload-card">
        <div className="upload-icon">↑</div>

        <h3>Upload Customer Dataset</h3>

        <p>
          Upload a CSV file containing customer information
          to generate batch churn predictions.
        </p>

        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          disabled={uploading}
        />

        {file && (
          <div className="selected-file">
            Selected: <strong>{file.name}</strong>
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={uploading || !file}
        >
          {uploading ? 'Analyzing Dataset...' : 'Upload & Predict'}
        </button>

        {error && (
          <div className="upload-error">
            {error}
          </div>
        )}
      </div>

      {results && (
        <div className="upload-results">

          <h3>Dataset Analysis Results</h3>

          <div className="upload-stats">

            <div className="upload-stat">
              <span>Total Customers</span>
              <strong>{results.total_rows}</strong>
            </div>

            <div className="upload-stat high">
              <span>High Risk</span>
              <strong>{results.high_risk_count}</strong>
            </div>

            <div className="upload-stat medium">
              <span>Medium Risk</span>
              <strong>{results.medium_risk_count}</strong>
            </div>

            <div className="upload-stat low">
              <span>Low Risk</span>
              <strong>{results.low_risk_count}</strong>
            </div>

          </div>

          <div className="table-wrapper">
            <table className="results-table">

              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Churn Risk</th>
                  <th>Status</th>
                  <th>Top Reason</th>
                  <th>Recommendation</th>
                </tr>
              </thead>

              <tbody>
                {results.predictions?.map((prediction, index) => (
                  <tr key={index}>
                    <td>Customer {prediction.row_number}</td>

                    <td>
                      {(prediction.churn_probability * 100).toFixed(1)}%
                    </td>

                    <td>
                      <span
                        className={
                          prediction.prediction === 'Churn'
                            ? 'status-risk'
                            : 'status-safe'
                        }
                      >
                        {prediction.prediction}
                      </span>
                    </td>

                    <td>{prediction.top_reason}</td>

                    <td>{prediction.recommendation}</td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>

          <a
            className="download-button"
            href="http://127.0.0.1:8000/download-results"
          >
            Download Full Results
          </a>

        </div>
      )}

    </div>
  );
}

export default DatasetUpload;