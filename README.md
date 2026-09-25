# Antarctic Ocean Risk-Aware Navigation and Iceberg Movement Prediction System

A beginner-friendly full-stack prototype using React/Vite/Three.js and
Python/FastAPI.

## Data warning

**SYNTHETIC DEMONSTRATION DATA — NOT REAL SCIENTIFIC OBSERVATIONS.**

The current generator is intentionally synthetic. The backend separates
generation from processing so a future real data provider can emit the same
data structures.

## Windows quick start

### Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_data.py
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

Open a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

FastAPI docs: http://localhost:8000/docs

## Architecture

Synthetic data -> risk engine + iceberg prediction -> risk-aware A* route
engine -> FastAPI JSON -> React + React Three Fiber -> 3D globe.

## Important prototype limitation

This system is for software demonstration and visualization. Its synthetic
iceberg predictions and routes are not scientifically validated and must not
be used for real-world Antarctic navigation.
