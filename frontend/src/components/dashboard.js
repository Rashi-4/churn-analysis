import React, { useEffect, useState } from 'react';
import './dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/dashboard-stats'
      );

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-message">
        Loading dashboard...
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="dashboard-message">
        Unable to load dashboard data.
      </div>
    );
  }

  return (
    <div className="dashboard">

      <div className="stats-grid">

        <div className="stat-card">
          <span>Total Predictions</span>
          <strong>{stats.total_predictions}</strong>
        </div>

        <div className="stat-card">
          <span>Average Churn Risk</span>
          <strong>
            {(stats.avg_churn_probability * 100).toFixed(1)}%
          </strong>
        </div>

        <div className="stat-card high">
          <span>High Risk</span>
          <strong>{stats.high_risk_count}</strong>
        </div>

      </div>

      <div className="recent-card">

        <div className="section-heading">
          <div>
            <h3>Recent Predictions</h3>
            <p>Latest customer churn predictions</p>
          </div>
        </div>

        {stats.recent_predictions?.length === 0 ? (
          <div className="no-data">
            No predictions have been made yet.
          </div>
        ) : (
          <div className="table-wrapper">

            <table className="dashboard-table">

              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Churn Risk</th>
                  <th>Risk Level</th>
                  <th>Recommendation</th>
                </tr>
              </thead>

              <tbody>
                {stats.recent_predictions?.map((prediction, index) => {

                  const probability =
                    prediction.churn_probability;

                  let level = 'LOW';

                  if (probability > 0.7) {
                    level = 'HIGH';
                  } else if (probability > 0.4) {
                    level = 'MEDIUM';
                  }

                  return (
                    <tr key={index}>

                      <td>{prediction.customer_id}</td>

                      <td>
                        {(probability * 100).toFixed(1)}%
                      </td>

                      <td>
                        <span className={`risk-${level.toLowerCase()}`}>
                          {level}
                        </span>
                      </td>

                      <td>
                        {prediction.recommendation}
                      </td>

                    </tr>
                  );
                })}
              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  );
}

export default Dashboard;