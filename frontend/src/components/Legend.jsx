export default function Legend({ selectedLayer, statistics }) {
  return (
    <section className="legend-card">
      <div className="legend-title">SELECTED PARAMETER</div>
      <div className="legend-parameter">{selectedLayer.label}</div>

      <div className="gradient-bar" />

      <div className="gradient-labels">
        <span>Low</span>
        <span>High</span>
      </div>

      <div className="statistics-grid">
        <div>
          <span>Minimum</span>
          <strong>{statistics.minimum}</strong>
        </div>
        <div>
          <span>Maximum</span>
          <strong>{statistics.maximum}</strong>
        </div>
        <div>
          <span>Average</span>
          <strong>{statistics.average}</strong>
        </div>
      </div>

      <div className="small-note">
        Values are computed from the current synthetic dataset.
      </div>
    </section>
  );
}
