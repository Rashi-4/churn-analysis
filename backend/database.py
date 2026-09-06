"""
Database operations for storing predictions
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from config import DATABASE_URL

class Database:
    def __init__(self, db_path=DATABASE_URL):
        self.db_path = db_path
        self.setup_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def setup_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                churn_probability REAL,
                reason_1 TEXT,
                reason_2 TEXT,
                reason_3 TEXT,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Model performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                accuracy REAL,
                f1_score REAL,
                recall REAL,
                precision REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Action log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                prediction_id INTEGER,
                action_taken TEXT,
                action_outcome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(prediction_id) REFERENCES predictions(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Database initialized")

    def save_prediction(self, customer_id, churn_prob, reasons, recommendation):
        """Save prediction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO predictions 
            (customer_id, churn_probability, reason_1, reason_2, reason_3, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            float(churn_prob),
            reasons[0]['factor'] if len(reasons) > 0 else "N/A",
            reasons[1]['factor'] if len(reasons) > 1 else "N/A",
            reasons[2]['factor'] if len(reasons) > 2 else "N/A",
            recommendation
        ))

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def get_recent_predictions(self, limit=10):
        """Get recent predictions"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, customer_id, churn_probability, reason_1, 
                   reason_2, reason_3, recommendation, created_at
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()
        return results

    def save_model_performance(self, model_name, accuracy, f1, recall, precision):
        """Save model performance metrics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO model_performance 
            (model_name, accuracy, f1_score, recall, precision)
            VALUES (?, ?, ?, ?, ?)
        ''', (model_name, accuracy, f1, recall, precision))

        conn.commit()
        conn.close()

# Create global database instance
db = Database()