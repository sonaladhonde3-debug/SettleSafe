export default function AlertTable({ alerts }) {
  if (!alerts.length) {
    return <p className="empty-state">No high-risk trades flagged yet.</p>;
  }

  return (
    <table className="alert-table">
      <thead>
        <tr>
          <th>Trade ID</th>
          <th>Risk Score</th>
          <th>Hard Rule Breach</th>
          <th>Violations</th>
          <th>Evaluated At</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert) => (
          <tr key={alert.assessment_id} className={alert.hard_rule_breach ? "row-critical" : "row-warning"}>
            <td>{alert.trade_id}</td>
            <td>{(alert.risk_score * 100).toFixed(2)}%</td>
            <td>{alert.hard_rule_breach ? "YES" : "No"}</td>
            <td>
              {alert.violations.length
                ? alert.violations.map((v) => v.code).join(", ")
                : "—"}
            </td>
            <td>{new Date(alert.evaluated_at).toLocaleTimeString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
