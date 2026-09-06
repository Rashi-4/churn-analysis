
import shap
import pickle
import pandas as pd
import numpy as np
from config import MODEL_PATH, TRAIN_DATA_PATH
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

class ChurnExplainer:
    def __init__(self, model_path=MODEL_PATH):
        self.model = None
        self.explainer = None
        self.X_train = None
        self.load_model(model_path)

    def load_model(self, model_path):
        print(f"Loading model from {model_path}...")
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        print("✓ Model loaded")

        # Load training data for SHAP
        train_data = pd.read_csv(TRAIN_DATA_PATH)
        self.X_train = train_data.drop('Churn', axis=1)

        # Create SHAP explainer
        print("Initializing SHAP explainer...")
        if isinstance(self.model, (RandomForestClassifier, GradientBoostingClassifier)):
          self.explainer = shap.TreeExplainer(self.model)
        else:
          self.explainer = shap.Explainer(self.model, self.X_train)

        print("✓ SHAP explainer ready")

    def explain_prediction(self, customer_data):
        """Explain prediction for a customer"""
        # Convert to DataFrame if dict
        if isinstance(customer_data, dict):
            customer_df = pd.DataFrame([customer_data])
        else:
            customer_df = customer_data

        # Get prediction
        prediction = self.model.predict(customer_df)[0]
        prediction_proba = self.model.predict_proba(customer_df)[0]
        churn_probability = prediction_proba[1]  # Probability of churn

        # Get SHAP explanation
        shap_output = self.explainer(customer_df)
        
        # Extract feature names and SHAP values
        feature_names = customer_df.columns.tolist()
        if hasattr(shap_output, "values"):
            values = shap_output.values
            if len(values.shape) == 3:
               shap_value = values[0, :, 1]
            else:
                shap_value = values[0]
        else:
           shap_value = shap_output[0]
       
        # Create reasons list
        reasons = []
        for i in range(len(feature_names)):
            reasons.append({
                'factor': feature_names[i],
                'impact': float(shap_value[i]),
                'customer_value': float(customer_df.iloc[0, i])
            })

        # Sort by absolute impact
        reasons = sorted(reasons, key=lambda x: abs(x['impact']), reverse=True)

        # Convert to plain language
        plain_reasons = self.convert_to_plain_language(reasons[:3])

        return {
            'prediction': int(prediction),
            'churn_probability': float(churn_probability),
            'top_reasons': plain_reasons[:3],
            'raw_shap': reasons
        }

    def convert_to_plain_language(self, reasons):
        """Convert SHAP values to plain business language"""
        plain_reasons = []

        for reason in reasons:
            factor = reason['factor']
            impact = reason['impact']
            value = reason['customer_value']

            # Determine direction
            direction = "increases" if impact > 0 else "decreases"
            impact_pct = abs(impact) * 100

            # Create plain text
            plain_text = f"{factor}: {impact_pct:.0f}% {direction} churn risk"

            plain_reasons.append({
                'factor': factor,
                'plain_text': plain_text,
                'impact': impact,
                'impact_percentage': impact_pct
            })

        return plain_reasons

    def get_recommendation(self, reasons):
        """Get retention recommendation based on reasons"""
        if not reasons:
            return "Contact for customer satisfaction survey"

        top_reason = reasons[0]['factor'].lower()

        # Rule-based recommendations
        if 'month' in top_reason and 'charge' in top_reason:
            return "Offer 20% discount on monthly charges or premium service upgrade"
        
        elif 'tenure' in top_reason or 'month' in top_reason:
            return "Enroll in loyalty program or provide welcome back incentive"
        
        elif 'contract' in top_reason:
            return "Recommend switching to longer-term contract with incentives"
        
        elif 'internet' in top_reason or 'service' in top_reason:
            return "Escalate to support team for service quality improvement"
        
        elif 'payment' in top_reason:
            return "Offer alternative payment methods or auto-pay discount"
        
        else:
            return "Conduct customer satisfaction survey"


def main():
    explainer = ChurnExplainer()
    
    test_customer = explainer.X_train.iloc[0].to_dict()

    result = explainer.explain_prediction(test_customer)

    print("\nPrediction Result:")
    print(f"Churn Probability: {result['churn_probability']:.0%}")

    print("\nTop Reasons:")
    for reason in result['top_reasons']:
        print(f"  - {reason['plain_text']}")

        
if __name__ == "__main__":
    main()