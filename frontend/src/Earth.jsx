import { useMemo } from "react";
import * as THREE from "three";
import { Line, OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";

const EARTH_RADIUS = 3;

function latLonToVector3(latitude, longitude, radius = EARTH_RADIUS) {
  // Latitude and longitude are converted from degrees to radians before
  // placing the point on a Three.js sphere.
  const latitudeRadians = THREE.MathUtils.degToRad(latitude);
  const longitudeRadians = THREE.MathUtils.degToRad(longitude);

  const x = radius * Math.cos(latitudeRadians) * Math.cos(longitudeRadians);
  const y = radius * Math.sin(latitudeRadians);
  const z = radius * Math.cos(latitudeRadians) * Math.sin(longitudeRadians);

  return new THREE.Vector3(x, y, z);
}

function valueRange(points, layerId) {
  const values = points.map((point) => {
    if (layerId === "iceberg_movement") {
      return point.iceberg_speed;
    }
    return point[layerId];
  });

  return {
    minimum: Math.min(...values),
    maximum: Math.max(...values),
  };
}

function interpolateColor(value, minimum, maximum) {
  const normalized =
    maximum === minimum
      ? 0.5
      : (value - minimum) / (maximum - minimum);

  const clamped = Math.max(0, Math.min(1, normalized));

  // Blue -> green -> yellow -> orange -> red.
  const stops = [
    new THREE.Color("#2563eb"),
    new THREE.Color("#22c55e"),
    new THREE.Color("#facc15"),
    new THREE.Color("#f97316"),
    new THREE.Color("#ef4444"),
  ];

  const scaled = clamped * (stops.length - 1);
  const index = Math.min(Math.floor(scaled), stops.length - 2);
  const amount = scaled - index;

  return stops[index].clone().lerp(stops[index + 1], amount);
}

function createGridLines() {
  const lines = [];

  for (let latitude = -90; latitude <= 90; latitude += 15) {
    const points = [];
    for (let longitude = -180; longitude <= 180; longitude += 4) {
      points.push(latLonToVector3(latitude, longitude, EARTH_RADIUS + 0.015));
    }
    lines.push({
      key: `lat-${latitude}`,
      points,
    });
  }

  for (let longitude = -180; longitude < 180; longitude += 15) {
    const points = [];
    for (let latitude = -90; latitude <= 90; latitude += 3) {
      points.push(latLonToVector3(latitude, longitude, EARTH_RADIUS + 0.015));
    }
    lines.push({
      key: `lon-${longitude}`,
      points,
    });
  }

  return lines;
}

function EnvironmentPoints({ points, selectedLayer, onPointSelect }) {
  const geometryData = useMemo(() => {
    if (!points.length) {
      return {
        positions: new Float32Array(),
        colors: new Float32Array(),
      };
    }

    const range = valueRange(points, selectedLayer);

    const positions = [];
    const colors = [];

    points.forEach((point) => {
      const position = latLonToVector3(
        point.latitude,
        point.longitude,
        EARTH_RADIUS + 0.06
      );

      const value =
        selectedLayer === "iceberg_movement"
          ? point.iceberg_speed
          : point[selectedLayer];

      const color = interpolateColor(
        value,
        range.minimum,
        range.maximum
      );

      positions.push(position.x, position.y, position.z);
      colors.push(color.r, color.g, color.b);
    });

    return {
      positions: new Float32Array(positions),
      colors: new Float32Array(colors),
    };
  }, [points, selectedLayer]);

  function handlePointerDown(event) {
    event.stopPropagation();

    if (!points.length) {
      return;
    }

    const pointIndex = event.index;
    const point = points[pointIndex];

    if (point) {
      onPointSelect(point);
    }
  }

  return (
    <points onPointerDown={handlePointerDown}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[geometryData.positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[geometryData.colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.055}
        vertexColors
        transparent
        opacity={0.88}
        sizeAttenuation
      />
    </points>
  );
}

function GlobeGrid() {
  const lines = useMemo(() => createGridLines(), []);

  return (
    <group>
      {lines.map((line) => (
        <Line
          key={line.key}
          points={line.points}
          color="#4b7898"
          transparent
          opacity={0.35}
          lineWidth={0.5}
        />
      ))}
    </group>
  );
}

function Marker({ latitude, longitude, color, size = 0.11 }) {
  const position = latLonToVector3(
    latitude,
    longitude,
    EARTH_RADIUS + 0.18
  );

  return (
    <mesh position={position}>
      <sphereGeometry args={[size, 12, 12]} />
      <meshBasicMaterial color={color} />
    </mesh>
  );
}

function RouteLine({ route }) {
  if (!route || route.length < 2) {
    return null;
  }

  const points = route.map((coordinate) =>
    latLonToVector3(
      coordinate.latitude,
      coordinate.longitude,
      EARTH_RADIUS + 0.2
    )
  );

  return (
    <Line
      points={points}
      color="#ffffff"
      lineWidth={3}
      transparent
      opacity={0.95}
    />
  );
}

function IcebergVisuals({ icebergs, selectedIceberg, onIcebergSelect }) {
  return (
    <group>
      {icebergs.map((iceberg) => {
        const currentPosition = latLonToVector3(
          iceberg.latitude,
          iceberg.longitude,
          EARTH_RADIUS + 0.2
        );

        const predictions = iceberg.prediction?.predictions || [];
        const pathPoints = [
          currentPosition,
          ...predictions.map((prediction) =>
            latLonToVector3(
              prediction.latitude,
              prediction.longitude,
              EARTH_RADIUS + 0.21
            )
          ),
        ];

        const isSelected = selectedIceberg?.id === iceberg.id;

        return (
          <group key={iceberg.id}>
            <mesh
              position={currentPosition}
              onPointerDown={(event) => {
                event.stopPropagation();
                onIcebergSelect(iceberg);
              }}
            >
              <sphereGeometry args={[isSelected ? 0.14 : 0.09, 10, 10]} />
              <meshBasicMaterial color="#dffcff" />
            </mesh>

            {pathPoints.length > 1 && (
              <Line
                points={pathPoints}
                color="#58e0ff"
                lineWidth={1.5}
                dashed
                dashSize={0.08}
                gapSize={0.06}
                transparent
                opacity={0.75}
              />
            )}

            {predictions.map((prediction) => (
              <Marker
                key={`${iceberg.id}-${prediction.hours}`}
                latitude={prediction.latitude}
                longitude={prediction.longitude}
                color="#67e8f9"
                size={0.045}
              />
            ))}
          </group>
        );
      })}
    </group>
  );
}

function StartAndDestination({ routeResult }) {
  if (!routeResult || !routeResult.route?.length) {
    return null;
  }

  const start = routeResult.route[0];
  const destination = routeResult.route[routeResult.route.length - 1];

  return (
    <group>
      <Marker
        latitude={start.latitude}
        longitude={start.longitude}
        color="#ffffff"
        size={0.13}
      />
      <Marker
        latitude={destination.latitude}
        longitude={destination.longitude}
        color="#ff4d8d"
        size={0.13}
      />
    </group>
  );
}

function AntarcticHighlight() {
  return (
    <mesh
      position={latLonToVector3(-82, 0, EARTH_RADIUS + 0.02)}
      rotation={[0, 0, 0]}
    >
      <circleGeometry args={[0.95, 48]} />
      <meshBasicMaterial
        color="#b7f5ff"
        transparent
        opacity={0.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function GlobeScene({
  points,
  selectedLayer,
  icebergs,
  selectedIceberg,
  onPointSelect,
  onIcebergSelect,
  routeResult,
}) {
  return (
    <>
      <ambientLight intensity={1.2} />

      <mesh>
        <sphereGeometry args={[EARTH_RADIUS, 64, 64]} />
        <meshStandardMaterial
          color="#082238"
          roughness={0.95}
          metalness={0.05}
        />
      </mesh>

      <GlobeGrid />
      <AntarcticHighlight />

      <EnvironmentPoints
        points={points}
        selectedLayer={selectedLayer}
        onPointSelect={onPointSelect}
      />

      <IcebergVisuals
        icebergs={icebergs}
        selectedIceberg={selectedIceberg}
        onIcebergSelect={onIcebergSelect}
      />

      <RouteLine route={routeResult?.route} />
      <StartAndDestination routeResult={routeResult} />
    </>
  );
}

export default function Earth({
  points,
  selectedLayer,
  icebergs,
  selectedIceberg,
  onPointSelect,
  onIcebergSelect,
  routeResult,
}) {
  return (
    <div className="earth-shell">
      <div className="earth-title">
        <span>LIVE PROTOTYPE VIEW</span>
        <strong>3D Antarctic Globe</strong>
      </div>

      <div className="earth-overlay">
        <div>LAT / LON GRID</div>
        <div>ICEBERG TRACKS</div>
        <div>RISK-AWARE ROUTING</div>
      </div>

      <CanvasCameraScene
        points={points}
        selectedLayer={selectedLayer}
        icebergs={icebergs}
        selectedIceberg={selectedIceberg}
        onPointSelect={onPointSelect}
        onIcebergSelect={onIcebergSelect}
        routeResult={routeResult}
      />

      <div className="earth-help">
        Drag to rotate • Scroll to zoom • Click an iceberg for predictions
      </div>
    </div>
  );
}

function CanvasCameraScene(props) {
  // This is the main React Three Fiber scene. OrbitControls provides the
  // interactive rotation and zoom requested by the prototype.
  return (
    <Canvas
      camera={{ position: [0, 0.2, 7.4], fov: 45 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true }}
    >
      <GlobeScene {...props} />
      <OrbitControls
        enablePan={false}
        minDistance={4.3}
        maxDistance={12}
        enableDamping
        dampingFactor={0.08}
      />
    </Canvas>
  );
}
