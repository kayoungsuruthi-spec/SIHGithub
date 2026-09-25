function riskClass(level) {
  if (level === "LOW") {
    return "risk-low";
  }
  if (level === "MEDIUM") {
    return "risk-medium";
  }
  if (level === "HIGH") {
    return "risk-high";
  }
  return "risk-extreme";
}

export default function RiskPanel({ routeResult }) {
  if (!routeResult) {
    return (
      <section className="panel">
        <div className="panel-heading">
          <span className="panel-index">03</span>
          <div>
            <h2>Route Result</h2>
            <p>Calculate a route to see risk-aware navigation details.</p>
          </div>
        </div>

        <div className="empty-state">
          No route calculated yet.
        </div>
      </section>
    );
  }

  return (
    <section className="panel route-result">
      <div className="route-success">SAFE ROUTE FOUND</div>

      <div className="route-stat-grid">
        <div>
          <span>Distance</span>
          <strong>{routeResult.total_distance_km} km</strong>
        </div>
        <div>
          <span>Average Risk</span>
          <strong>{routeResult.average_risk}%</strong>
        </div>
        <div>
          <span>Maximum Risk</span>
          <strong>{routeResult.maximum_risk}%</strong>
        </div>
        <div>
          <span>Environmental Cost</span>
          <strong>{routeResult.environmental_cost}</strong>
        </div>
      </div>

      <div className={`route-risk ${riskClass(routeResult.route_risk_level)}`}>
        Risk Level: {routeResult.route_risk_level}
      </div>

      <h3>Factors Considered</h3>
      <ul className="factor-list">
        {routeResult.factors_considered.map((factor) => (
          <li key={factor}>✓ {factor}</li>
        ))}
      </ul>

      <div className="small-note">{routeResult.note}</div>
    </section>
  );
}
