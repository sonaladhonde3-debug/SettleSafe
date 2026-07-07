<div align="center">
  <h1>🚀 Real-Time FinTech Risk Engine</h1>
  <p>
    <b>An enterprise-grade, real-time machine learning pipeline for detecting settlement risks in equity markets.</b>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python" />
    <img src="https://img.shields.io/badge/React-18-blue.svg" alt="React" />
    <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI" />
    <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Scikit--Learn-1.3-orange.svg" alt="Scikit-Learn" />
  </p>
</div>

<br/>

## 📖 Overview

In modern clearing houses and brokerage firms, millions of trades execute per second. If a client leverages their account heavily and fails to settle a massive trade during volatile market conditions, the broker absorbs the catastrophic loss. 

This project is a **Full-Stack FinTech Risk Prediction Terminal**. It simulates a live exchange feed, ingests trade data in real-time via WebSockets, and evaluates the probability of a settlement failure using a dual-engine architecture:
1. **Deterministic Hard Rules Engine:** Instantly flags illegal behaviors (e.g., Margin Utilization > 100%).
2. **AI Probability Engine:** A heavily regularized Random Forest classifier that detects nuanced, high-risk human behavior patterns (AUC ~0.87).

## ✨ Key Features

- **Live WebSocket Streaming:** Trades are evaluated by the FastAPI backend and instantly streamed to the React dashboard via WebSockets.
- **Persistent Audit Trail:** Every evaluated trade, along with its ML probability score and hard-rule violations, is permanently archived in a **PostgreSQL** database using SQLAlchemy.
- **Live Market Hooks:** The Python simulator fetches live `^INDIAVIX` data from the Yahoo Finance API to inject real-world macroeconomic volatility into the risk evaluations.
- **Premium Glassmorphism UI:** A state-of-the-art React terminal featuring deep space gradients, frosted glass panels, and neon-glowing CSS keyframe animations for critical alerts.
- **Production-Ready ML Pipeline:** Includes scripts for synthetic data generation, irreducible noise injection (label flipping), and hyperparameter regularization to prevent dataset memorization (overfitting).

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| **Frontend** | React (Vite), HTML5, Vanilla CSS (Glassmorphism), WebSockets |
| **Backend** | Python, FastAPI, Uvicorn, SQLAlchemy, psycopg2 |
| **Database** | PostgreSQL |
| **Data Science** | Pandas, NumPy, Scikit-Learn (Random Forest Classifier) |
| **Data Integrations** | `yfinance` (Live Yahoo Finance API) |

## 📂 Project Architecture

```text
real-time-risk-predictor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py      # FastAPI Routes
│   │   │   └── websockets.py     # WebSocket Handlers
│   │   ├── core/
│   │   │   ├── model.py          # ML Inference Engine
│   │   │   └── rules.py          # Deterministic Hard Rules
│   │   ├── db/
│   │   │   ├── database.py       # SQLAlchemy Setup
│   │   │   └── models.py         # DB Schemas & Tables
│   │   ├── utils/
│   │   │   └── processors.py     # Data Transformers
│   │   ├── config.py             # App Configuration
│   │   └── main.py               # FastAPI Entrypoint
│   ├── data/                     # Synthetic Datasets
│   ├── models/                   # Serialized Scikit-Learn .pkl
│   └── scripts/
│       ├── generate_settlement_risk_dataset.py
│       ├── inject_noise.py       # Chaos stress-testing
│       ├── train_model_rf.py     # Random Forest Training
│       └── simulate_trades.py    # Live WebSocket Producer
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AlertTable.jsx
│   │   │   ├── ManualTradeForm.jsx
│   │   │   ├── ManualTradeForm.css
│   │   │   └── RiskChart.jsx
│   │   ├── hooks/                # Custom React Hooks
│   │   ├── App.jsx               # Main React Dashboard
│   │   └── App.css               # Premium Glassmorphism UI
│   └── package.json
├── .env                          # DB Credentials
└── start_all.bat                 # 1-Click Startup Script
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL Server running locally

### 2. Database Setup
Create a PostgreSQL database and update your `.env` files in both the `frontend` and `backend` directories.
```env
# backend/.env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/risk_db
```

### 3. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 4. Train the ML Model
Before starting the server, you must train the Random Forest AI.
```bash
python backend/scripts/generate_settlement_risk_dataset.py
python backend/scripts/inject_noise.py
python backend/scripts/train_model_rf.py
```

### 5. Launch the Terminal
Simply double-click the `start_all.bat` file in the root directory! This will automatically launch the FastAPI backend, the React frontend, and the Live Trade Simulator all at once.

Navigate to `http://localhost:5173` to view the live dashboard.

## 🔮 Future Enhancements
- **Apache Kafka:** Migrate from WebSockets to Kafka topics (`trades_raw` and `trades_evaluated`) for horizontal scalability.
- **Dockerization:** Wrap the entire stack (PostgreSQL, FastAPI, React) into a `docker-compose.yml` for true 1-click deployment.
- **Explainable AI (XAI):** Integrate the `SHAP` library so the API returns exact feature attributions (e.g., "Why did this trade score 92% risk?").

