function valueForLayer(point, layerId) {
  if (!point) {
    return null;
  }

  if (layerId === "iceberg_movement") {
    return point.iceberg_speed;
  }

  return point[layerId];
}

function formatValue(value, layerId) {
  if (value === null || value === undefined) {
    return "—";
  }

  if (
    layerId === "temperature" ||
    layerId === "salinity" ||
    layerId === "current_speed" ||
    layerId === "wind_speed" ||
    layerId === "iceberg_speed"
  ) {
    return Number(value).toFixed(2);
  }

  return `${Number(value).toFixed(1)}%`;
}

export default function DataPanel({
  selectedLayer,
  selectedPoint,
  selectedIceberg,
}) {
  const currentValue = valueForLayer(selectedPoint, selectedLayer.id);

  return (
    <section className="panel data-panel">
      <div className="panel-heading">
        <span className="panel-index">04</span>
        <div>
          <h2>Environmental Information</h2>
          <p>{selectedLayer.label}</p>
        </div>
      </div>

      <div className="focus-value">
        <span>Current value</span>
        <strong>{formatValue(currentValue, selectedLayer.id)}</strong>
      </div>

      {selectedPoint && (
        <div className="coordinate-readout">
          <span>Grid position</span>
          <strong>
            {selectedPoint.latitude.toFixed(1)}°,{" "}
            {selectedPoint.longitude.toFixed(1)}°
          </strong>
        </div>
      )}

      {selectedIceberg && (
        <div className="iceberg-details">
          <div className="iceberg-title">ICEBERG {selectedIceberg.id}</div>
          <div className="iceberg-row">
            <span>Position</span>
            <strong>
              {selectedIceberg.latitude}°, {selectedIceberg.longitude}°
            </strong>
          </div>
          <div className="iceberg-row">
            <span>Speed</span>
            <strong>{selectedIceberg.prediction?.movement_speed ?? selectedIceberg.speed} km/h</strong>
          </div>
          <div className="iceberg-row">
            <span>Direction</span>
            <strong>{selectedIceberg.prediction?.movement_direction ?? selectedIceberg.direction}°</strong>
          </div>

          {selectedIceberg.prediction?.predictions?.map((prediction) => (
            <div className="iceberg-row" key={prediction.hours}>
              <span>{prediction.hours}h prediction</span>
              <strong>
                {prediction.latitude}°, {prediction.longitude}°
              </strong>
            </div>
          ))}
        </div>
      )}

      <div className="small-note">
        Synthetic demonstration data — not real scientific observations.
      </div>
    </section>
  );
}
