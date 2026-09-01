# HouseValue

HouseValue estimates Mumbai residential-property prices with a FastAPI service, a LightGBM model and the React interface in `frontend`.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Backend\requirements.txt
Copy-Item Backend\.env.example Backend\.env
.\.venv\Scripts\python.exe -m uvicorn app:app --app-dir Backend --reload --port 8000

cd frontend
npm install
npm run dev
```

The frontend uses `http://127.0.0.1:8000` by default. Copy `frontend/.env.example` to `frontend/.env` only when the API is hosted elsewhere.

## Docker and PostgreSQL

Set non-default `POSTGRES_PASSWORD` and `JWT_SECRET` values in `docker-compose.yml` before any shared deployment, then run:

```powershell
docker compose up --build
```

This serves the React app on port 5173 and FastAPI on port 8000. Local development uses SQLite automatically; set `DATABASE_URL` to a PostgreSQL connection string for a durable deployment.

## MLOps

`cleaned_data.csv`, the LightGBM model and KMeans model are DVC outputs. Set up an approved remote before sharing data or models:

```powershell
pip install dvc
dvc remote add -d storage <your-approved-DVC-remote>
dvc push
```

Restore artefacts after a clone with `dvc pull`. CI runs API tests, builds the UI and rejects model changes whose deterministic evaluation sample drops below R² 0.50. The full workflow is in `.github/workflows/ci.yml`.

The feedback endpoint records actual prices. Once 1,000 records are marked `verified`, it queues a retraining job in the database. Run `python Backend/ml/retrain.py` in a worker environment to create a DVC-trackable candidate model; only promote a candidate after review.

## Model card

| Item | Detail |
| --- | --- |
| Model | LightGBM regressor (`lightgbm-mumbai-v1`) |
| Intended use | Indicative price estimates for Mumbai residential properties |
| Training data | `Data/cleaned_data.csv`, Mumbai listings and associated location data |
| Inputs | Area, locality, property type, BHK, bathrooms, furnishing, floors, pincode, coordinates and distances to selected Mumbai hubs |
| Current validation | Notebook-recorded tuned LightGBM R²: 0.8692; CI applies an independent regression guardrail |
| Outputs | Estimated INR price, confidence and optional live neighbourhood signals |

### Limitations and responsible use

- This is an estimate, not a valuation, loan decision, tax assessment or investment recommendation.
- Accuracy is weaker for unseen localities, properties above 5,000 sq ft, prices above ₹10 crore, incomplete records and markets outside Mumbai.
- The current saved model was not trained with live amenity counts or Walk Score. Those signals are returned to users and added to the feedback/retraining pipeline; they must not be treated as causal price inputs until the next model is trained and evaluated with them.
- Market inflation and concept drift can make historic training data stale. Review model performance and feature drift before promoting a candidate model.

See [the architecture diagram](docs/architecture.md) for the data flow.
