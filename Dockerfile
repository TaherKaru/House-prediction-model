FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY Backend/requirements.txt /app/Backend/requirements.txt
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt
COPY Backend /app/Backend
COPY Data/cleaned_data.csv /app/Data/cleaned_data.csv
COPY Data/models/lightgbm.pkl /app/Data/models/lightgbm.pkl
COPY Data/models/kmeans.pkl /app/Data/models/kmeans.pkl

WORKDIR /app/Backend
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
