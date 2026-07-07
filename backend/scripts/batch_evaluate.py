import pickle
import pandas as pd
from pathlib import Path
import sys

# Append backend directory to sys.path so we can import from app
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.core.rules import evaluate_hard_rules, has_hard_breach
from app.config import settings

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "settlement_risk_synthetic_dataset.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "random_forest.pkl"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "batch_evaluation_results.csv"

def main():
    if not DATA_PATH.exists():
        print(f"Error: Dataset not found at {DATA_PATH}")
        return
        
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    print("Loading model...")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # We don't need the ground truth for prediction
    if "settlement_fail" in df.columns:
        X = df.drop(columns=["settlement_fail", "trade_id"])
    else:
        X = df.drop(columns=["trade_id"])

    print(f"Evaluating {len(df)} trades instantly...")
    
    # Run ML prediction on the entire batch at once
    risk_scores = model.predict_proba(X)[:, 1]
    
    results = []
    high_risk_count = 0
    hard_breach_count = 0
    
    # Combine ML scores with Hard Rules
    for i, row in df.iterrows():
        trade_dict = row.to_dict()
        score = risk_scores[i]
        
        violations = evaluate_hard_rules(trade_dict)
        hard_breach = has_hard_breach(violations)
        
        is_high_risk = hard_breach or score >= settings.HIGH_RISK_PROBABILITY_THRESHOLD
        
        if is_high_risk:
            high_risk_count += 1
        if hard_breach:
            hard_breach_count += 1
            
        results.append({
            "trade_id": row["trade_id"],
            "risk_score_percentage": round(score * 100, 2),
            "is_high_risk": is_high_risk,
            "hard_rule_breach": hard_breach,
            "rule_violations": ", ".join([v.code for v in violations]) if violations else "None"
        })
        
    # Save results
    results_df = pd.DataFrame(results)
    
    # Combine with original features
    final_df = pd.merge(df, results_df, on="trade_id")
    final_df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "="*40)
    print("🎯 BATCH EVALUATION COMPLETE")
    print("="*40)
    print(f"Total Trades Evaluated : {len(df)}")
    print(f"Total Safe Trades      : {len(df) - high_risk_count}")
    print(f"Total High Risk Trades : {high_risk_count}")
    print(f"  ↳ Triggered by ML    : {high_risk_count - hard_breach_count}")
    print(f"  ↳ Triggered by Rules : {hard_breach_count}")
    print("="*40)
    print(f"Detailed results saved to:\n{OUTPUT_PATH}")

if __name__ == "__main__":
    main()
