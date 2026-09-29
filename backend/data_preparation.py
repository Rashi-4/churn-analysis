import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
from pathlib import Path

from config import (
    DATASET_PATH, TRAIN_DATA_PATH, TEST_DATA_PATH,
    CATEGORICAL_FEATURES, NUMERICAL_FEATURES, TEST_SIZE, RANDOM_STATE
)

class DataPreparation:
    def __init__(self, dataset_path=DATASET_PATH):
        self.dataset_path = dataset_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.encoders = {}
        self.feature_names = None

    def load_data(self):
        """Load dataset from CSV"""
        print(f"Loading data from {self.dataset_path}...")
        self.df = pd.read_csv(self.dataset_path)
        self.df["TotalCharges"] = pd.to_numeric(
    self.df["TotalCharges"], errors="coerce"
)
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        return self.df

    def explore_data(self):
        """Explore dataset"""
        if self.df is None:
            self.load_data()

        print("\n=== DATA EXPLORATION ===")
        print(f"\nFirst 5 rows:\n{self.df.head()}")
        print(f"\nData types:\n{self.df.dtypes}")
        print(f"\nMissing values:\n{self.df.isnull().sum()}")
        print(f"\nBasic statistics:\n{self.df.describe()}")

        if 'Churn' in self.df.columns:
            print(f"\nChurn distribution:\n{self.df['Churn'].value_counts()}")
            print(f"Churn percentage: {self.df['Churn'].value_counts(normalize=True) * 100}")

    def clean_data(self):
        """Clean data"""
        print("\n=== DATA CLEANING ===")

        initial_shape = self.df.shape[0]
        self.df = self.df.drop_duplicates()
        print(f"Removed {initial_shape - self.df.shape[0]} duplicate rows")

        missing_count = self.df.isnull().sum().sum()
        if missing_count > 0:
            print(f"Found {missing_count} missing values")
           
            for col in self.df.select_dtypes(include=[np.number]).columns:
                self.df[col] = self.df[col].fillna(self.df[col].median())

            for col in self.df.select_dtypes(include=['object']).columns:
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
        else:
            print("No missing values found")

        cols_to_drop = ['customerID']
        cols_to_drop = [col for col in cols_to_drop if col in self.df.columns]
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            print(f"Dropped columns: {cols_to_drop}")

        print(f"Dataset shape after cleaning: {self.df.shape}")

    def encode_categorical(self):
        """Encode categorical variables"""
        print("\n=== ENCODING CATEGORICAL VARIABLES ===")

        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if 'Churn' in categorical_cols:
            categorical_cols.remove('Churn')

        print(f"Categorical columns: {categorical_cols}")

        for col in categorical_cols:
            encoder = LabelEncoder()
            self.df[col + '_encoded'] = encoder.fit_transform(self.df[col])
            self.encoders[col] = encoder
            print(f"Encoded {col}")

        # Encode target variable (Churn)
        if 'Churn' in self.df.columns:
            churn_encoder = LabelEncoder()
            self.df['Churn_encoded'] = churn_encoder.fit_transform(self.df['Churn'])
            self.encoders['Churn'] = churn_encoder

    def prepare_features_target(self):
        """Prepare features and target"""
        print("\n=== PREPARING FEATURES AND TARGET ===")

        # Drop original categorical columns, keep only encoded
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        self.df = self.df.drop(columns=categorical_cols)

        # Separate features and target
        self.X = self.df.drop(columns=['Churn_encoded'])
        self.y = self.df['Churn_encoded']

        self.feature_names = list(self.X.columns)
        print(f"Features: {self.feature_names}")
        print(f"Target: Churn_encoded")
        print(f"Features shape: {self.X.shape}")
        print(f"Target shape: {self.y.shape}")

    def split_data(self):
        """Split data into train and test"""
        print(f"\n=== SPLITTING DATA (Test size: {TEST_SIZE}) ===")

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=self.y
        )

        print(f"Training set: {self.X_train.shape[0]} samples")
        print(f"Testing set: {self.X_test.shape[0]} samples")
        print(f"Train churn rate: {self.y_train.mean():.2%}")
        print(f"Test churn rate: {self.y_test.mean():.2%}")

    def save_data(self):
        """Save prepared data"""
        print("\n=== SAVING PREPARED DATA ===")

        # Save train data
        train_data = self.X_train.copy()
        train_data['Churn'] = self.y_train
        train_data.to_csv(TRAIN_DATA_PATH, index=False)
        print(f"Saved training data to {TRAIN_DATA_PATH}")

        # Save test data
        test_data = self.X_test.copy()
        test_data['Churn'] = self.y_test
        test_data.to_csv(TEST_DATA_PATH, index=False)
        print(f"Saved test data to {TEST_DATA_PATH}")

        # Save encoders and feature names
        Path(TRAIN_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(Path(TRAIN_DATA_PATH).parent / "encoders.pkl", 'wb') as f:
            pickle.dump(self.encoders, f)
        with open(Path(TRAIN_DATA_PATH).parent / "feature_names.pkl", 'wb') as f:
            pickle.dump(self.feature_names, f)

        print("Saved encoders and feature names")

    def run_full_pipeline(self):
        """Run complete data preparation pipeline"""
        print("=" * 50)
        print("STARTING DATA PREPARATION PIPELINE")
        print("=" * 50)

        self.load_data()
        self.explore_data()
        self.clean_data()
        self.encode_categorical()
        self.prepare_features_target()
        self.split_data()
        self.save_data()

        print("\n" + "=" * 50)
        print("DATA PREPARATION COMPLETE")
        print("=" * 50)

        return self.X_train, self.X_test, self.y_train, self.y_test


def main():
    """Main entry point"""
    prep = DataPreparation()
    prep.run_full_pipeline()


if __name__ == "__main__":
    main()