#!/bin/bash
set -e

PROJECT_ID="the-golden-codex-1111"
SERVICE_NAME="artiswa-operator"
REGION="us-west1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
SA_NAME="artiswa-operator-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Artiswa Operator — Autonomous AI Artist Agent ==="
echo "Cloud Run + Claude Sonnet + X API + Firestore memory"
echo ""

# --- Service Account (least privilege) ---
echo "[1/5] Ensuring service account: ${SA_EMAIL}"
gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Artiswa Operator (autonomous poster)" \
    --project="${PROJECT_ID}"

# Firestore read/write (its memory + hash_index reads)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user" --quiet 2>/dev/null

# GCS read (download artwork images from archive bucket)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer" --quiet 2>/dev/null

# Secret Manager read (API keys)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" --quiet 2>/dev/null

echo "  Permissions: Firestore user, GCS viewer, Secret Manager accessor"
echo "  NO admin, NO delete, NO deploy, NO billing"

# --- Build ---
echo ""
echo "[2/5] Building container..."
gcloud builds submit --tag "${IMAGE}" --project="${PROJECT_ID}"

# --- Deploy ---
echo ""
echo "[3/5] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --timeout=120 \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},FIRESTORE_DB=golden-codex-database,ARCHIVE_BUCKET=codex-archive-bucket-dev" \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,X_CONSUMER_KEY=x-consumer-key:latest,X_CONSUMER_SECRET=x-consumer-secret:latest,X_ACCESS_TOKEN=artiswa-x-access-token:latest,X_ACCESS_TOKEN_SECRET=artiswa-x-access-token-secret:latest" \
  --no-allow-unauthenticated

# --- Cloud Scheduler (post every 45 minutes) ---
echo ""
echo "[4/5] Setting up Cloud Scheduler..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

gcloud scheduler jobs describe artiswa-post-cycle --location="${REGION}" --project="${PROJECT_ID}" 2>/dev/null && \
  gcloud scheduler jobs update http artiswa-post-cycle \
    --location="${REGION}" \
    --schedule="*/45 * * * *" \
    --uri="${SERVICE_URL}/post" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud scheduler jobs create http artiswa-post-cycle \
    --location="${REGION}" \
    --schedule="*/45 * * * *" \
    --uri="${SERVICE_URL}/post" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}"

echo ""
echo "[5/5] Verifying..."
echo "Service URL: ${SERVICE_URL}"
echo "Schedule: Every 45 minutes"
echo "Auth: Service account OIDC (no public access)"
echo ""
echo "=== Artiswa Operator deployed ==="
echo "She will begin posting autonomously on schedule."
echo "Monitor: ${SERVICE_URL}/session"
echo "Decisions: ${SERVICE_URL}/decisions"
