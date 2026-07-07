"""
================================================================================
 Synthetic T+1 Settlement Failure / Peak Margin Breach Risk Dataset Generator
--------------------------------------------------------------------------------
 Domain     : Indian Equity Cash Market (NSE Clearing Ltd / CCIL / SEBI T+1)
 Purpose    : Generate a production-grade synthetic dataset for testing a
              hybrid (deterministic-rule + ML) real-time settlement risk
              engine that predicts:
                 (a) T+1 settlement failures (auction / close-out triggers)
                 (b) Intra-day peak margin utilization breaches

 Author     : Quant Data Science / Database Architecture (synthetic gen)
 Notes      : All figures are illustrative synthetic data for engineering
              test purposes only. Not derived from any real counterparty
              or trade data. CPRA grading scheme, historical fail-rate
              bands, and margin multipliers are stylized approximations
              of CCIL/NCL/SEBI risk-management concepts for simulation.
================================================================================
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------------------
# 0. CONFIG
# ------------------------------------------------------------------------
N_ROWS = 50_000          # <-- change this to scale the dataset up/down
SEED = 42
rng = np.random.default_rng(SEED)

OUTPUT_CSV = "settlement_risk_synthetic_dataset.csv"

# ------------------------------------------------------------------------
# 1. trade_id
# ------------------------------------------------------------------------
trade_id = [f"TXN-IN-{100000 + i}" for i in range(N_ROWS)]

# ------------------------------------------------------------------------
# 2. india_vix : 11.0 - 45.0, slightly right-skewed
#    Gamma(shape=2.2, scale=3.6) -> then shifted/clipped into [11, 45]
# ------------------------------------------------------------------------
raw_vix = rng.gamma(shape=2.2, scale=3.6, size=N_ROWS)
india_vix = 11.0 + raw_vix
india_vix = np.clip(india_vix, 11.0, 45.0)
# round to 2 decimals like a real VIX print
india_vix = np.round(india_vix, 2)

# ------------------------------------------------------------------------
# 3. cpra_grade : CCIL-style Counterparty Risk Assessment grade
#    CPRA_1 Prime 60% | CPRA_2 Standard 25% | CPRA_3 Watchlist 12% | CPRA_4 High Risk 3%
# ------------------------------------------------------------------------
grade_labels = ["CPRA_1", "CPRA_2", "CPRA_3", "CPRA_4"]
grade_probs = [0.60, 0.25, 0.12, 0.03]
cpra_grade = rng.choice(grade_labels, size=N_ROWS, p=grade_probs)

# numeric risk weight used later for the hidden composite risk score
cpra_numeric_map = {"CPRA_1": 1, "CPRA_2": 2, "CPRA_3": 3, "CPRA_4": 4}
cpra_numeric = np.vectorize(cpra_numeric_map.get)(cpra_grade)

# ------------------------------------------------------------------------
# 4. historical_fail_rate : mathematically dependent on cpra_grade
#    CPRA_1 : 0.0001 - 0.005   (near zero)
#    CPRA_2 : 0.005  - 0.02    (standard, low-moderate)
#    CPRA_3 : 0.02   - 0.04    (watchlist, elevated)
#    CPRA_4 : 0.04   - 0.15    (high risk, heavy upward skew + gaussian noise)
# ------------------------------------------------------------------------
historical_fail_rate = np.zeros(N_ROWS)

masks = {
    "CPRA_1": (cpra_grade == "CPRA_1"),
    "CPRA_2": (cpra_grade == "CPRA_2"),
    "CPRA_3": (cpra_grade == "CPRA_3"),
    "CPRA_4": (cpra_grade == "CPRA_4"),
}

# CPRA_1 : tight near-zero band
n1 = masks["CPRA_1"].sum()
historical_fail_rate[masks["CPRA_1"]] = rng.uniform(0.0001, 0.005, n1)

# CPRA_2 : low-moderate band with small noise
n2 = masks["CPRA_2"].sum()
base2 = rng.uniform(0.005, 0.02, n2)
historical_fail_rate[masks["CPRA_2"]] = base2 + rng.normal(0, 0.002, n2)

# CPRA_3 : watchlist, elevated band with moderate noise
n3 = masks["CPRA_3"].sum()
base3 = rng.uniform(0.02, 0.04, n3)
historical_fail_rate[masks["CPRA_3"]] = base3 + rng.normal(0, 0.004, n3)

# CPRA_4 : high risk, heavy upward skew + gaussian noise
n4 = masks["CPRA_4"].sum()
base4 = rng.uniform(0.04, 0.15, n4)
historical_fail_rate[masks["CPRA_4"]] = base4 + np.abs(rng.normal(0, 0.015, n4))

# clip to a sane [0, 0.20] band and round
historical_fail_rate = np.clip(historical_fail_rate, 0.0001, 0.20)
historical_fail_rate = np.round(historical_fail_rate, 5)

# ------------------------------------------------------------------------
# 5. trade_size_inr : Log-Normal -> many small retail/HNI trades under 5L,
#    long right tail with institutional block trades > 5 Cr (5,00,00,000)
# ------------------------------------------------------------------------
# mu/sigma tuned in log-space so median trade ~ INR 1.5-2L, with tail > 5Cr
mu_log = 12.2      # exp(12.2) ~ 199,000 (median-ish)
sigma_log = 1.55   # controls tail heaviness

trade_size_inr = rng.lognormal(mean=mu_log, sigma=sigma_log, size=N_ROWS)
# floor very small trades at a realistic minimum (~ INR 5,000)
trade_size_inr = np.clip(trade_size_inr, 5_000, None)
trade_size_inr = np.round(trade_size_inr, 2)

BLOCK_TRADE_THRESHOLD = 5_00_00_000  # INR 5 Crore
is_block_trade = (trade_size_inr > BLOCK_TRADE_THRESHOLD).astype(int)

# ------------------------------------------------------------------------
# 6. epi_flag : Early Pay-In flag, ~40% of trades
# ------------------------------------------------------------------------
epi_flag = rng.binomial(1, 0.40, size=N_ROWS)

# ------------------------------------------------------------------------
# 7. peak_margin_utilization : Beta distribution peaked ~0.60
#    Beta(a=6, b=4) has mean = a/(a+b) = 0.6
#    Stress multiplier: if india_vix > 30 -> scale by 1.25x
#    Force a small set of extreme outlier rows > 1.0 (active breach)
# ------------------------------------------------------------------------
peak_margin_utilization = rng.beta(a=6, b=4, size=N_ROWS)

stress_mask = india_vix > 30
peak_margin_utilization[stress_mask] = peak_margin_utilization[stress_mask] * 1.25

# inject a small set (~1.5%) of hard outlier breach rows, mostly amongst
# already-stressed / high-risk rows, pushed decisively above 1.0
outlier_pool = np.where(
    (india_vix > 28) | (cpra_grade == "CPRA_4") | (cpra_grade == "CPRA_3")
)[0]
n_outliers = max(1, int(0.015 * N_ROWS))
if len(outlier_pool) > 0:
    outlier_idx = rng.choice(outlier_pool, size=min(n_outliers, len(outlier_pool)), replace=False)
    peak_margin_utilization[outlier_idx] = rng.uniform(1.02, 1.45, size=len(outlier_idx))

peak_margin_utilization = np.round(peak_margin_utilization, 4)

# ------------------------------------------------------------------------
# 8. settlement_fail : hidden composite risk score -> percentile threshold
#    -> ~2-3% positive class, EPI=1 collapses probability to ~0
# ------------------------------------------------------------------------
# Normalize each risk driver to roughly [0, 1] before weighting
cpra_component = (cpra_numeric - 1) / 3.0                     # 0,0.33,0.67,1.0
hist_fail_component = historical_fail_rate / historical_fail_rate.max()
vix_component = (india_vix - 11.0) / (45.0 - 11.0)
block_component = is_block_trade.astype(float)                # 0 or 1

# small amount of idiosyncratic noise so the score isn't a deterministic
# linear formula an ML model could trivially invert
noise = rng.normal(0, 0.03, N_ROWS)

risk_score = (
    0.35 * cpra_component
    + 0.30 * hist_fail_component
    + 0.20 * vix_component
    + 0.15 * block_component
    + noise
)

# Critical exception: EPI executed -> assets already locked in by the CC,
# so failure probability collapses to ~0 regardless of the base score.
risk_score_final = np.where(epi_flag == 1, risk_score * 0.001, risk_score)

# Enforce class imbalance: top ~2.5% of the *final* (EPI-adjusted) risk
# score across the WHOLE dataset becomes settlement_fail = 1. Because
# EPI=1 rows are suppressed near zero, they almost never clear the cut.
fail_threshold = np.percentile(risk_score_final, 97.5)
settlement_fail = (risk_score_final > fail_threshold).astype(int)

# ------------------------------------------------------------------------
# Assemble final DataFrame
# ------------------------------------------------------------------------
df = pd.DataFrame({
    "trade_id": trade_id,
    "india_vix": india_vix,
    "cpra_grade": cpra_grade,
    "historical_fail_rate": historical_fail_rate,
    "trade_size_inr": trade_size_inr,
    "epi_flag": epi_flag,
    "peak_margin_utilization": peak_margin_utilization,
    "settlement_fail": settlement_fail,
})

df.to_csv(OUTPUT_CSV, index=False)

# ------------------------------------------------------------------------
# Quick validation summary (printed, not part of the CSV)
# ------------------------------------------------------------------------
print(f"Rows generated                : {len(df):,}")
print(f"settlement_fail positive rate : {df['settlement_fail'].mean()*100:.2f}%")
print(f"cpra_grade distribution:\n{df['cpra_grade'].value_counts(normalize=True).round(3)}")
print(f"india_vix range                : {df['india_vix'].min()} - {df['india_vix'].max()}")
print(f"trade_size_inr median           : {df['trade_size_inr'].median():,.0f}")
print(f"trade_size_inr > 5Cr count      : {(df['trade_size_inr'] > 5_00_00_000).sum()}")
print(f"epi_flag rate                   : {df['epi_flag'].mean()*100:.2f}%")
print(f"fail rate when epi_flag==1      : {df.loc[df.epi_flag==1,'settlement_fail'].mean()*100:.4f}%")
print(f"fail rate when epi_flag==0      : {df.loc[df.epi_flag==0,'settlement_fail'].mean()*100:.2f}%")
print(f"peak_margin_utilization >1.0    : {(df['peak_margin_utilization']>1.0).sum()}")
print(f"Saved to                        : {OUTPUT_CSV}")
