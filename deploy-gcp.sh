#!/usr/bin/env bash
# Usage: ./deploy-gcp.sh  (after editing the variables below and running `gcloud auth login`)
set -euo pipefail
PROJECT_ID="your-gcp-project-id"
REGION="asia-south1"
INSTANCE="ai-learning-db"
SERVICE="ai-learning"
BUCKET="${PROJECT_ID}-learning-files"
DB_PASS="change-this-db-password"
LLM_KEY="your-groq-or-gemini-key"

gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# MySQL on Cloud SQL
gcloud sql instances create "$INSTANCE" --database-version=MYSQL_8_0 --tier=db-f1-micro --region="$REGION" || true
gcloud sql databases create ai_learning --instance="$INSTANCE" || true
gcloud sql users create ailearn --instance="$INSTANCE" --password="$DB_PASS" || true

# Cloud Storage bucket for resources
gsutil mb -l "$REGION" "gs://$BUCKET" || true

CONN="$PROJECT_ID:$REGION:$INSTANCE"
gcloud run deploy "$SERVICE" --source . --region "$REGION" --allow-unauthenticated \
  --add-cloudsql-instances "$CONN" \
  --set-env-vars "DATABASE_URL=mysql+pymysql://ailearn:${DB_PASS}@/ai_learning?unix_socket=/cloudsql/${CONN},GCS_BUCKET=${BUCKET},LLM_API_KEY=${LLM_KEY},LLM_BASE_URL=https://api.groq.com/openai/v1,LLM_MODEL=llama-3.1-8b-instant,SECRET_KEY=$(openssl rand -hex 24),JWT_SECRET_KEY=$(openssl rand -hex 24),CORS_ORIGINS=*"
echo "Deployed. Open the URL printed above."
