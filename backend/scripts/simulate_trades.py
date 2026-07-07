import time
import random
import requests
import pandas as pd
from pathlib import Path

# Use 127.0.0.1 instead of localhost to avoid IPv6 issues on Windows
API_URL = "http://127.0.0.1:8000/api/v1/trades/evaluate"
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "settlement_risk_synthetic_dataset.csv"

# Cache for live VIX
LIVE_VIX_CACHE = None
LIVE_VIX_LAST_FETCH = 0

def get_live_vix():
    global LIVE_VIX_CACHE, LIVE_VIX_LAST_FETCH
    now = time.time()
    
    # Refresh cache every 60 seconds
    if LIVE_VIX_CACHE is None or (now - LIVE_VIX_LAST_FETCH) > 60:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^INDIAVIX"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            LIVE_VIX_CACHE = float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
            LIVE_VIX_LAST_FETCH = now
            print(f"--- Fetched Live India VIX: {LIVE_VIX_CACHE} ---")
        except Exception as e:
            print(f"Warning: Could not fetch live VIX ({e}). Using synthetic fallback.")
            
    return LIVE_VIX_CACHE

def main():
    if not DATA_PATH.exists():
        print(f"Dataset not found at {DATA_PATH}")
        return

    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    if "settlement_fail" in df.columns:
        df = df.drop(columns=["settlement_fail"])

    print(f"Starting sequential trade simulation, sending to {API_URL}...")
    for index, row in df.iterrows():
        
        # Try to get live VIX, otherwise fallback to the CSV row's VIX
        live_vix = get_live_vix()
        final_vix = live_vix if live_vix is not None else float(row["india_vix"])
        
        # Convert numpy types to native python types for JSON serialization
        trade = {
            "trade_id": str(row["trade_id"]),
            "india_vix": final_vix,
            "cpra_grade": str(row["cpra_grade"]),
            "historical_fail_rate": float(row["historical_fail_rate"]),
            "trade_size_inr": float(row["trade_size_inr"]),
            "epi_flag": int(row["epi_flag"]),
            "peak_margin_utilization": float(row["peak_margin_utilization"]),
        }
        
        try:
            resp = requests.post(API_URL, json=trade)
            if resp.status_code == 200:
                result = resp.json()
                print(f"Trade {trade['trade_id']} evaluated: risk_score={result['risk_score']}, high_risk={result['is_high_risk']} (VIX used: {final_vix})")
            else:
                print(f"Error evaluating trade: {resp.status_code} {resp.text}")
        except requests.exceptions.ConnectionError:
            print("Failed to connect to API. Is uvicorn running on 127.0.0.1:8000?")
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    main()
