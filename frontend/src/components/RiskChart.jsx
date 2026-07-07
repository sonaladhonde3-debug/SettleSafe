import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

/**
 * Time-series plot of incoming risk scores. Expects alerts newest-first;
 * the chart reverses them so time flows left-to-right.
 */
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const alert = data.alertDetails;
    const details = alert.trade_details || {};
    
    return (
      <div className="custom-tooltip" style={{ backgroundColor: "#1e293b", padding: "12px", border: "1px solid #334155", borderRadius: "8px", color: "#f8fafc", fontSize: "13px", minWidth: "220px", boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)" }}>
        <p style={{ margin: "0 0 8px 0", fontWeight: "600", color: "#94a3b8" }}>Time: {label}</p>
        <p style={{ margin: "0 0 12px 0", color: "#ef4444", fontSize: "15px", fontWeight: "bold" }}>Risk Score: {data.riskScore}%</p>
        
        {details.trade_id && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px 12px", borderTop: "1px solid #334155", paddingTop: "10px" }}>
            <span style={{ color: "#94a3b8" }}>Trade ID:</span> <span>{details.trade_id}</span>
            <span style={{ color: "#94a3b8" }}>India VIX:</span> <span>{details.india_vix}</span>
            <span style={{ color: "#94a3b8" }}>CPRA Grade:</span> <span>{details.cpra_grade}</span>
            <span style={{ color: "#94a3b8" }}>Hist Fail Rate:</span> <span>{(details.historical_fail_rate * 100).toFixed(1)}%</span>
            <span style={{ color: "#94a3b8" }}>Trade Size:</span> <span>₹{details.trade_size_inr}</span>
            <span style={{ color: "#94a3b8" }}>EPI Executed:</span> <span>{details.epi_flag ? 'Yes' : 'No'}</span>
            <span style={{ color: "#94a3b8" }}>Margin Util:</span> <span>{(details.peak_margin_utilization * 100).toFixed(1)}%</span>
          </div>
        )}
        
        {alert.hard_rule_breach && alert.violations && (
          <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px solid #334155" }}>
            <p style={{ margin: "0 0 4px 0", color: "#fca5a5", fontWeight: "600" }}>⚠️ Rule Breaches:</p>
            <ul style={{ margin: 0, paddingLeft: "16px", color: "#fca5a5" }}>
              {alert.violations.map((v, i) => <li key={i}>{v.code}</li>)}
            </ul>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function RiskChart({ alerts }) {
  const data = [...alerts]
    .slice(0, 50)
    .reverse()
    .map((alert) => ({
      time: new Date(alert.evaluated_at).toLocaleTimeString(),
      riskScore: Number((alert.risk_score * 100).toFixed(2)),
      alertDetails: alert,
    }));

  if (!data.length) {
    return <p className="empty-state">Waiting for risk data...</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} unit="%" />
        <Tooltip content={<CustomTooltip />} />
        <Line type="monotone" dataKey="riskScore" stroke="#dc2626" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
