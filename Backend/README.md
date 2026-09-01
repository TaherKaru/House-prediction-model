# HouseValue FastAPI backend

This FastAPI API stores accounts, feedback and retraining jobs through SQLAlchemy.
It uses SQLite locally and PostgreSQL when `DATABASE_URL` is supplied.

## Configure

Copy `.env.example` to a new file called `.env` inside this folder. For PostgreSQL,
set a connection string such as:

```env
DATABASE_URL=postgresql+psycopg://housevalue:password@127.0.0.1:5432/housevalue
JWT_SECRET=replace-with-a-long-random-secret
```

Without `DATABASE_URL`, `housevalue.db` is created automatically.

## Run

```powershell
.\.venv\Scripts\python.exe -m pip install -r Backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --app-dir Backend --reload --port 8000
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Security used

- Passwords are BCrypt hashes; plain-text passwords are never stored.
- JWT is required for `/api/predict` and `/api/feedback`.
- `/api/predict` loads the packaged LightGBM and KMeans artefacts from `Data/models`.
