import { useState } from "react";
import "./ManualTradeForm.css";

export default function ManualTradeForm() {
  const [formData, setFormData] = useState({
    trade_id: `MANUAL-${Math.floor(Math.random() * 10000)}`,
    india_vix: "",
    cpra_grade: "CPRA_1",
    historical_fail_rate: "",
    trade_size_inr: "",
    epi_flag: "0",
    peak_margin_utilization: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      trade_id: formData.trade_id,
      india_vix: parseFloat(formData.india_vix),
      cpra_grade: formData.cpra_grade,
      historical_fail_rate: parseFloat(formData.historical_fail_rate),
      trade_size_inr: parseFloat(formData.trade_size_inr),
      epi_flag: parseInt(formData.epi_flag, 10),
      peak_margin_utilization: parseFloat(formData.peak_margin_utilization),
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/trades/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
      // Generate a new random ID for the next trade
      setFormData((prev) => ({
        ...prev,
        trade_id: `MANUAL-${Math.floor(Math.random() * 10000)}`,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="manual-form-container">
      <form onSubmit={handleSubmit} className="manual-form">
        <div className="form-grid">
          <div className="form-group">
            <label>India VIX</label>
            <input
              type="number"
              step="0.01"
              name="india_vix"
              value={formData.india_vix}
              onChange={handleChange}
              placeholder="e.g. 15.5"
              required
            />
          </div>

          <div className="form-group">
            <label>CPRA Grade</label>
            <select name="cpra_grade" value={formData.cpra_grade} onChange={handleChange} required>
              <option value="CPRA_1">CPRA_1 (Low Risk)</option>
              <option value="CPRA_2">CPRA_2</option>
              <option value="CPRA_3">CPRA_3</option>
              <option value="CPRA_4">CPRA_4 (High Risk)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Historical Fail Rate</label>
            <input
              type="number"
              step="0.001"
              name="historical_fail_rate"
              value={formData.historical_fail_rate}
              onChange={handleChange}
              placeholder="e.g. 0.05"
              required
            />
          </div>

          <div className="form-group">
            <label>Trade Size (INR)</label>
            <input
              type="number"
              name="trade_size_inr"
              value={formData.trade_size_inr}
              onChange={handleChange}
              placeholder="e.g. 500000"
              required
            />
          </div>

          <div className="form-group">
            <label>EPI Flag (Early Pay-In)</label>
            <select name="epi_flag" value={formData.epi_flag} onChange={handleChange} required>
              <option value="0">No (0)</option>
              <option value="1">Yes (1)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Peak Margin Utilization</label>
            <input
              type="number"
              step="0.01"
              name="peak_margin_utilization"
              value={formData.peak_margin_utilization}
              onChange={handleChange}
              placeholder="e.g. 0.85"
              required
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="evaluate-btn">
          {loading ? "Evaluating..." : "Evaluate Trade"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className={`result-card ${result.is_high_risk ? "high-risk" : "safe"}`}>
          <h3>Prediction Result</h3>
          <div className="result-metric">
            <span>Risk Score:</span>
            <strong>{(result.risk_score * 100).toFixed(2)}%</strong>
          </div>
          <div className="result-metric">
            <span>Status:</span>
            <strong>
              {result.is_high_risk ? "🚨 HIGH RISK (Flagged)" : "✅ SAFE (Expected to Clear)"}
            </strong>
          </div>
          {result.hard_rule_breach && (
            <div className="rule-breach">
              ⚠️ Hard Rule Breach Detected
              <ul>
                {result.violations.map((v, i) => (
                  <li key={i}>{v.message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
