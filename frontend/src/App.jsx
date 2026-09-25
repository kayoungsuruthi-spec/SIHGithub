import { useEffect, useMemo, useState } from "react";
import Earth from "./Earth";
import {
  calculateRoute,
  generateSyntheticData,
  getEnvironmentalData,
  getIcebergs,
  getSummary,
} from "./api";
import Header from "./components/Header";
import LayerPanel, { layerDefinitions } from "./components/LayerPanel";
import RoutePanel from "./components/RoutePanel";
import RiskPanel from "./components/RiskPanel";
import Legend from "./components/Legend";
import DataPanel from "./components/DataPanel";

const variableLabels = {
  temperature: "Temperature",
  salinity: "Salinity",
  current_speed: "Ocean Current",
  sea_ice: "Sea Ice",
  iceberg_probability: "Iceberg Probability",
  iceberg_movement: "Iceberg Movement",
  weather_risk: "Weather Risk",
  weather_change_risk: "Sudden Weather Change",
  risk: "Overall Risk",
};

const defaultStatistics = {
  minimum: "—",
  maximum: "—",
  average: "—",
};

function calculateStatistics(points, selectedLayer) {
  if (!points.length) {
    return defaultStatistics;
  }

  const values = points.map((point) => {
    if (selectedLayer === "iceberg_movement") {
      return Number(point.iceberg_speed);
    }
    return Number(point[selectedLayer]);
  });

  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const average = values.reduce((total, value) => total + value, 0) / values.length;

  return {
    minimum: minimum.toFixed(2),
    maximum: maximum.toFixed(2),
    average: average.toFixed(2),
  };
}

function selectRepresentativePoint(points, selectedLayer) {
  if (!points.length) {
    return null;
  }

  const middleIndex = Math.floor(points.length / 2);
  const sorted = [...points].sort((first, second) => {
    const firstValue =
      selectedLayer === "iceberg_movement"
        ? first.iceberg_speed
        : first[selectedLayer];

    const secondValue =
      selectedLayer === "iceberg_movement"
        ? second.iceberg_speed
        : second[selectedLayer];

    return Number(secondValue) - Number(firstValue);
  });

  return sorted[middleIndex] || points[0];
}

export default function App() {
  const [selectedLayer, setSelectedLayer] = useState("risk");
  const [points, setPoints] = useState([]);
  const [icebergs, setIcebergs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [routeResult, setRouteResult] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [selectedIceberg, setSelectedIceberg] = useState(null);

  const [loading, setLoading] = useState(true);
  const [routeLoading, setRouteLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const selectedLayerDefinition = useMemo(() => {
    return (
      layerDefinitions.find((layer) => layer.id === selectedLayer) ||
      layerDefinitions[0]
    );
  }, [selectedLayer]);

  const statistics = useMemo(() => {
    return calculateStatistics(points, selectedLayer);
  }, [points, selectedLayer]);

  async function loadDashboard() {
    setLoading(true);
    setErrorMessage("");

    try {
      const [dataResponse, icebergResponse, summaryResponse] =
        await Promise.all([
          getEnvironmentalData(),
          getIcebergs(),
          getSummary(),
        ]);

      setPoints(dataResponse.points);
      setIcebergs(icebergResponse.icebergs);
      setSummary(summaryResponse);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  function handleLayerChange(layer) {
    setSelectedLayer(layer);

    const point = selectRepresentativePoint(points, layer);
    setSelectedPoint(point);
  }

  async function handleGenerate() {
    setGenerating(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const response = await generateSyntheticData();
      await loadDashboard();
      setSuccessMessage(
        `New synthetic demonstration dataset generated with seed ${response.seed}.`
      );
      setRouteResult(null);
      setSelectedIceberg(null);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleRoute(start, destination) {
    setRouteLoading(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      if (
        start.latitude < -90 ||
        start.latitude > -60 ||
        destination.latitude < -90 ||
        destination.latitude > -60
      ) {
        throw new Error(
          "Both start and destination latitudes must be between -90 and -60."
        );
      }

      const result = await calculateRoute(start, destination);
      setRouteResult(result);
      setSuccessMessage("Risk-aware route calculated successfully.");
    } catch (error) {
      setRouteResult(null);
      setErrorMessage(error.message);
    } finally {
      setRouteLoading(false);
    }
  }

  function handlePointSelect(point) {
    setSelectedPoint(point);
    setSelectedIceberg(null);
  }

  function handleIcebergSelect(iceberg) {
    setSelectedIceberg(iceberg);
    setSelectedPoint(null);
  }

  const overallRisk = summary?.overall_risk?.average ?? "—";
  const icebergRisk = summary?.iceberg_risk?.average ?? "—";
  const weatherRisk = summary?.weather_risk?.average ?? "—";
  const temperature = summary?.temperature?.average ?? "—";
  const salinity = summary?.salinity?.average ?? "—";

  return (
    <div className="app">
      <Header onGenerate={handleGenerate} generating={generating} />

      {errorMessage && (
        <div className="message error-message">
          <strong>Attention:</strong> {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="message success-message">{successMessage}</div>
      )}

      <div className="summary-grid">
        <SummaryCard label="Temperature" value={`${temperature} °C`} />
        <SummaryCard label="Salinity" value={salinity} />
        <SummaryCard label="Iceberg Risk" value={`${icebergRisk}%`} />
        <SummaryCard label="Weather Risk" value={`${weatherRisk}%`} />
        <SummaryCard label="Overall Risk" value={`${overallRisk}%`} />
      </div>

      <main className="dashboard-grid">
        <aside className="left-column">
          <LayerPanel
            selectedLayer={selectedLayer}
            onLayerChange={handleLayerChange}
          />

          <RoutePanel
            onCalculate={handleRoute}
            loading={routeLoading}
          />

          <RiskPanel routeResult={routeResult} />
        </aside>

        <section className="center-column">
          <Earth
            points={points}
            selectedLayer={selectedLayer}
            icebergs={icebergs}
            selectedIceberg={selectedIceberg}
            onPointSelect={handlePointSelect}
            onIcebergSelect={handleIcebergSelect}
            routeResult={routeResult}
          />
        </section>

        <aside className="right-column">
          <Legend
            selectedLayer={selectedLayerDefinition}
            statistics={statistics}
          />

          <DataPanel
            selectedLayer={selectedLayerDefinition}
            selectedPoint={selectedPoint}
            selectedIceberg={selectedIceberg}
          />

          <section className="panel system-status">
            <div className="panel-heading">
              <span className="panel-index">05</span>
              <div>
                <h2>System Status</h2>
                <p>Prototype service health.</p>
              </div>
            </div>

            <div className="status-row">
              <span>Environmental grid</span>
              <strong>{loading ? "LOADING" : `${points.length} POINTS`}</strong>
            </div>

            <div className="status-row">
              <span>Iceberg objects</span>
              <strong>{icebergs.length}</strong>
            </div>

            <div className="status-row">
              <span>Selected layer</span>
              <strong>{variableLabels[selectedLayer]}</strong>
            </div>

            <div className="small-note">
              Synthetic demonstration data — not real scientific observations.
            </div>
          </section>
        </aside>
      </main>

      <footer className="app-footer">
        <span>ANTARCTIC OCEAN INTELLIGENCE</span>
        <span>Prototype • Risk-aware visualization • Synthetic data</span>
      </footer>
    </div>
  );
}

function SummaryCard({ label, value }) {
  return (
    <div className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
