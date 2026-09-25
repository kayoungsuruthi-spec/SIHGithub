const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function requestJson(url, options = {}) {
  try {
    const response = await fetch(url, options);

    const contentType = response.headers.get("content-type") || "";

    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const message =
        typeof payload === "object" && payload?.detail
          ? payload.detail
          : "The backend returned an error.";

      throw new Error(message);
    }

    return payload;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        "Unable to connect to the backend. Please check that the FastAPI server is running."
      );
    }

    throw error;
  }
}

export async function getEnvironmentalData(variable = null) {
  const query = variable
    ? `?variable=${encodeURIComponent(variable)}`
    : "";

  return requestJson(`${API_BASE_URL}/data${query}`);
}

export async function generateSyntheticData(seed = null) {
  const generatedSeed =
    seed === null
      ? Math.floor(Math.random() * 1000000000)
      : seed;

  return requestJson(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      seed: generatedSeed,
    }),
  });
}

export async function getSummary() {
  return requestJson(`${API_BASE_URL}/summary`);
}

export async function getIcebergs() {
  return requestJson(`${API_BASE_URL}/icebergs`);
}

export async function predictIceberg(
  icebergId,
  hours = [6, 12, 24, 48]
) {
  return requestJson(`${API_BASE_URL}/icebergs/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      iceberg_id: icebergId,
      hours,
    }),
  });
}

export async function calculateRoute(start, destination) {
  return requestJson(`${API_BASE_URL}/route`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start,
      destination,
    }),
  });
}

export async function getRisk() {
  return requestJson(`${API_BASE_URL}/risk`);
}