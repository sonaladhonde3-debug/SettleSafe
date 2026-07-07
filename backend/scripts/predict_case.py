import pickle
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "gradient_boost.pkl"

def main():
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        print("Please run 'python scripts/train_model.py' first.")
        return

    print("Loading trained model...")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    print("\n--- Enter Trade Details ---")
    
    trade_id = input("Trade ID (e.g., TXN-123): ")
    
    try:
        india_vix = float(input("India VIX (e.g., 15.5): "))
        cpra_grade = input("CPRA Grade (CPRA_1, CPRA_2, CPRA_3, or CPRA_4): ").strip().upper()
        historical_fail_rate = float(input("Historical Fail Rate (e.g., 0.05 for 5%): "))
        trade_size_inr = float(input("Trade Size in INR (e.g., 500000): "))
        epi_flag = int(input("EPI Flag (1 for True, 0 for False): "))
        peak_margin_utilization = float(input("Peak Margin Utilization (e.g., 0.85): "))
    except ValueError:
        print("\nError: Invalid number format entered. Please try again.")
        return

    # Create a DataFrame with a single row
    features = {
        "india_vix": india_vix,
        "cpra_grade": cpra_grade,
        "historical_fail_rate": historical_fail_rate,
        "trade_size_inr": trade_size_inr,
        "epi_flag": epi_flag,
        "peak_margin_utilization": peak_margin_utilization,
    }
    
    df = pd.DataFrame([features])
    
    # Predict
    proba = model.predict_proba(df)[0][1]
    is_high_risk = proba >= 0.65  # The threshold used in the app

    print("\n--- Prediction Results ---")
    print(f"Risk Score (Probability of Failure): {proba * 100:.2f}%")
    
    if is_high_risk:
        print("Prediction: YES (High Risk / Settlement Fail Expected) 🚨")
    else:
        print("Prediction: NO (Safe / Settlement Expected to Clear) ✅")

if __name__ == "__main__":
    main()
