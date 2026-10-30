# ---- build React ----
FROM node:20-alpine AS fe
WORKDIR /fe
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Flask + built frontend (Cloud Run) ----
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY --from=fe /fe/dist frontend/dist
WORKDIR /app/backend
ENV PORT=8080 PYTHONUNBUFFERED=1
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 run:app
