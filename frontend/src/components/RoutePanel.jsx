import { useState } from "react";

function CoordinateInput({
  label,
  latitude,
  longitude,
  onLatitudeChange,
  onLongitudeChange,
}) {
  return (
    <div className="coordinate-group">
      <div className="coordinate-label">{label}</div>

      <label>
        Latitude
        <input
          type="number"
          step="0.1"
          min="-90"
          max="-60"
          value={latitude}
          onChange={(event) => onLatitudeChange(event.target.value)}
        />
      </label>

      <label>
        Longitude
        <input
          type="number"
          step="0.1"
          min="-180"
          max="180"
          value={longitude}
          onChange={(event) => onLongitudeChange(event.target.value)}
        />
      </label>
    </div>
  );
}

export default function RoutePanel({ onCalculate, loading }) {
  const [startLatitude, setStartLatitude] = useState("-65");
  const [startLongitude, setStartLongitude] = useState("20");
  const [destinationLatitude, setDestinationLatitude] = useState("-70");
  const [destinationLongitude, setDestinationLongitude] = useState("70");

  function submitRoute(event) {
    event.preventDefault();

    onCalculate(
      {
        latitude: Number(startLatitude),
        longitude: Number(startLongitude),
      },
      {
        latitude: Number(destinationLatitude),
        longitude: Number(destinationLongitude),
      }
    );
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <span className="panel-index">02</span>
        <div>
          <h2>Route Navigation</h2>
          <p>Risk-aware A* planning inside the Antarctic prototype grid.</p>
        </div>
      </div>

      <form onSubmit={submitRoute}>
        <CoordinateInput
          label="START"
          latitude={startLatitude}
          longitude={startLongitude}
          onLatitudeChange={setStartLatitude}
          onLongitudeChange={setStartLongitude}
        />

        <CoordinateInput
          label="DESTINATION"
          latitude={destinationLatitude}
          longitude={destinationLongitude}
          onLatitudeChange={setDestinationLatitude}
          onLongitudeChange={setDestinationLongitude}
        />

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Calculating..." : "Calculate Safe Route"}
        </button>
      </form>

      <div className="small-note">
        Coordinates must be between -90° and -60° latitude.
      </div>
    </section>
  );
}
