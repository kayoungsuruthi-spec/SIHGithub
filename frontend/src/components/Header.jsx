export default function Header({ onGenerate, generating }) {
  return (
    <header className="app-header">
      <div>
        <div className="eyebrow">OCEAN RISK INTELLIGENCE / PROTOTYPE</div>
        <h1>ANTARCTIC OCEAN INTELLIGENCE</h1>
        <p>
          Environmental Monitoring • Iceberg Prediction • Risk-Aware Navigation
        </p>
        <div className="data-warning">
          SYNTHETIC DEMONSTRATION DATA — NOT REAL SCIENTIFIC OBSERVATIONS
        </div>
      </div>

      <button
        className="secondary-button"
        type="button"
        onClick={onGenerate}
        disabled={generating}
      >
        {generating ? "Generating..." : "Generate New Synthetic Data"}
      </button>
    </header>
  );
}
