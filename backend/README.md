# Antarctic Ocean Risk-Aware Navigation — Backend

This FastAPI backend provides synthetic Antarctic environmental data,
iceberg movement prediction, risk scoring, and a risk-aware A* route.

## Demonstration data warning

All current data is SYNTHETIC DEMONSTRATION DATA. It is not real scientific
observation data and must not be used for real navigation.

## Windows setup

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_data.py
python -m uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Future data provider

The API boundary is intentionally separated from the generator. A future
implementation can add a real provider that produces the same point and
iceberg dictionary shape. Possible sources include Copernicus Marine, NOAA,
NASA Earth observation products, ECMWF, and Sentinel-derived products.
