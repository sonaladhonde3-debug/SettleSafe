"""
Generates a Random Forest model using the Indian Equity Cash Market synthetic dataset.

Usage:
    python backend/scripts/train_model_rf.py
"""
import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "settlement_risk_synthetic_dataset.csv"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "models" / "random_forest.pkl"


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["trade_id", "settlement_fail"])
    y = df["settlement_fail"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    categorical_features = ["cpra_grade"]
    numeric_features = [
        "india_vix", 
        "historical_fail_rate", 
        "trade_size_inr", 
        "epi_flag", 
        "peak_margin_utilization"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    # Use Random Forest instead of Gradient Boosting
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                max_depth=5,
                min_samples_leaf=20,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            )),
        ]
    )

    print("Training Random Forest model...")
    model.fit(X_train, y_train)

    test_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, test_proba)
    print(f"Validation AUC: {auc:.4f} (positive class prevalence: {y.mean():.4%})")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
