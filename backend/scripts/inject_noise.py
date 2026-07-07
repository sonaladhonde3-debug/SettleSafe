import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "settlement_risk_synthetic_dataset.csv"

def inject_noise():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    np.random.seed(42)
    
    # 1. Label Flipping (1% of data)
    # Randomly invert the success/fail result on 1% of trades
    # This represents irreducible human error (unpredictable chaos)
    flip_indices = np.random.choice(df.index, size=int(len(df) * 0.01), replace=False)
    df.loc[flip_indices, 'settlement_fail'] = 1 - df.loc[flip_indices, 'settlement_fail']
    
    # 2. Gaussian Noise Injection
    # Add random statistical fuzziness (+/- 5%) to margin utilization
    noise = np.random.normal(loc=0, scale=0.05, size=len(df))
    df['peak_margin_utilization'] = df['peak_margin_utilization'] + noise
    # Ensure margin doesn't drop below 0
    df['peak_margin_utilization'] = df['peak_margin_utilization'].clip(lower=0.0) 
    
    # Save the chaotic dataset
    df.to_csv(DATA_PATH, index=False)
    print(f"Successfully injected chaos and label-flipping noise into {len(df)} rows!")
    print(f"Overwrote {DATA_PATH}")

if __name__ == "__main__":
    inject_noise()
