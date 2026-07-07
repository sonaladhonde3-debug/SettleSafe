import { useWebSocket } from "./hooks/useWebSocket";
import AlertTable from "./components/AlertTable";
import RiskChart from "./components/RiskChart";
import ManualTradeForm from "./components/ManualTradeForm";
import "./App.css";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000/ws/alerts";

export default function App() {
  const { alerts, connectionStatus } = useWebSocket(WS_URL);

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Real-Time Margin Call &amp; Settlement Fail Monitor</h1>
        <span className={`status-badge status-${connectionStatus}`}>{connectionStatus}</span>
      </header>

      <div className="main-grid">
        <aside className="left-panel">
          <section className="panel">
            <h2>Manual Trade Entry</h2>
            <ManualTradeForm />
          </section>
        </aside>

        <main className="right-panel">
          <section className="panel">
            <h2>Risk Score Trend (Live Stream)</h2>
            <RiskChart alerts={alerts} />
          </section>

          <section className="panel">
            <h2>Flagged Trades (Live Stream)</h2>
            <AlertTable alerts={alerts} />
          </section>
        </main>
      </div>
    </div>
  );
}
