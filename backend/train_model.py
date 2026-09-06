
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

import pickle
from pathlib import Path
from config import (
    TRAIN_DATA_PATH, TEST_DATA_PATH, MODEL_DIR, MODEL_PATH, RANDOM_STATE
)
from database import db

class ModelTrainer:
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.best_model = None
        self.best_model_name = None

    def load_data(self):
        """Load preprocessed data"""
        print("Loading preprocessed data...")
        
        train_data = pd.read_csv(TRAIN_DATA_PATH)
        test_data = pd.read_csv(TEST_DATA_PATH)

        self.X_train = train_data.drop('Churn', axis=1)
        self.y_train = train_data['Churn']
        self.X_test = test_data.drop('Churn', axis=1)
        self.y_test = test_data['Churn']

        print(f"X_train shape: {self.X_train.shape}")
        print(f"X_test shape: {self.X_test.shape}")

    def train_logistic_regression(self):
        """Train Logistic Regression"""
        print("\n=== TRAINING LOGISTIC REGRESSION ===")
        model = LogisticRegression(max_iter=3000, random_state=RANDOM_STATE)
        model.fit(self.X_train, self.y_train)
        self.models['Logistic Regression'] = model
        print("✓ Logistic Regression trained")

    def train_random_forest(self):
        """Train Random Forest"""
        print("\n=== TRAINING RANDOM FOREST ===")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
        model.fit(self.X_train, self.y_train)
        self.models['Random Forest'] = model
        print("✓ Random Forest trained")

    def train_gradient_boosting(self):
        """Train Gradient Boosting"""
        print("\n=== TRAINING GRADIENT BOOSTING ===")
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=RANDOM_STATE
        )
        model.fit(self.X_train, self.y_train)
        self.models['Gradient Boosting'] = model
        print("✓ Gradient Boosting trained")

    def evaluate_model(self, model, model_name):
        """Evaluate a single model"""
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]

        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        auc = roc_auc_score(self.y_test, y_pred_proba)

        print(f"\n{model_name} Results:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  ROC-AUC:   {auc:.4f}")

        return {
            'name': model_name,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc
        }

    def evaluate_all_models(self):
        """Evaluate all trained models"""
        print("\n" + "=" * 50)
        print("MODEL EVALUATION")
        print("=" * 50)

        results = []
        for model_name, model in self.models.items():
            result = self.evaluate_model(model, model_name)
            results.append(result)

        # Find best model (by F1-score)
        best = max(results, key=lambda x: x['f1'])
        self.best_model_name = best['name']
        self.best_model = self.models[best['name']]

        print(f"\n{'*' * 50}")
        print(f"BEST MODEL: {self.best_model_name}")
        print(f"F1-Score: {best['f1']:.4f}")
        print(f"{'*' * 50}")

        # Save performance to database
        db.save_model_performance(
            model_name=self.best_model_name,
            accuracy=best['accuracy'],
            f1=best['f1'],
            recall=best['recall'],
            precision=best['precision']
        )

        return results

    def save_model(self):
        """Save best model to file"""
        print(f"\nSaving {self.best_model_name} model...")
        
        # Create models directory
        Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

        # Save model
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.best_model, f)
        print(f"✓ Model saved to {MODEL_PATH}")

    def run_training_pipeline(self):
        """Run complete training pipeline"""
        print("=" * 50)
        print("STARTING MODEL TRAINING PIPELINE")
        print("=" * 50)

        self.load_data()
        self.train_logistic_regression()
        self.train_random_forest()
        self.train_gradient_boosting()
        self.evaluate_all_models()
        self.save_model()

        print("\n" + "=" * 50)
        print("MODEL TRAINING COMPLETE")
        print("=" * 50)


def main():
    """Main entry point"""
    trainer = ModelTrainer()
    trainer.run_training_pipeline()


if __name__ == "__main__":
    main()