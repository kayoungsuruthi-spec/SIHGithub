const layers = [
  { id: "temperature", label: "Temperature" },
  { id: "salinity", label: "Salinity" },
  { id: "current_speed", label: "Ocean Current" },
  { id: "sea_ice", label: "Sea Ice" },
  { id: "iceberg_probability", label: "Iceberg Probability" },
  { id: "iceberg_movement", label: "Iceberg Movement" },
  { id: "weather_risk", label: "Weather Risk" },
  { id: "weather_change_risk", label: "Sudden Weather Change" },
  { id: "risk", label: "Overall Risk" },
];

export const layerDefinitions = layers;

export default function LayerPanel({ selectedLayer, onLayerChange }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <span className="panel-index">01</span>
        <div>
          <h2>Environmental Layers</h2>
          <p>Select a variable to color the Antarctic grid.</p>
        </div>
      </div>

      <div className="layer-list">
        {layers.map((layer) => (
          <button
            key={layer.id}
            className={
              selectedLayer === layer.id
                ? "layer-button active"
                : "layer-button"
            }
            type="button"
            onClick={() => onLayerChange(layer.id)}
          >
            <span className="layer-dot" />
            {layer.label}
          </button>
        ))}
      </div>
    </section>
  );
}
