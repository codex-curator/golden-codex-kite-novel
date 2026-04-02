#!/bin/bash
set -e

PROJECT_ID="the-golden-codex-1111"
SERVICE_NAME="watchdog-agent"
REGION="us-west1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
SA_NAME="watchdog-agent-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Watchdog Agent — X Image Monitor + Licensing ==="
echo ""

# --- Service Account (least privilege) ---
echo "[1/4] Ensuring service account: ${SA_EMAIL}"
gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Watchdog Agent (X monitor + licensing)" \
    --project="${PROJECT_ID}"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user" --quiet 2>/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" --quiet 2>/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" --quiet 2>/dev/null

# --- Build ---
echo ""
echo "[2/4] Building container..."
gcloud builds submit --tag "${IMAGE}" --project="${PROJECT_ID}"

# --- Deploy ---
echo ""
echo "[3/4] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --timeout=120 \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},FIRESTORE_DB=golden-codex-database,WATCHDOG_AGENT_ID=watchdog-agent-01,AEGIS_URL=https://aegis-agent-172867820131.us-west1.run.app,KITE_FACILITATOR_URL=https://facilitator.pieverse.io,KITE_SETTLEMENT_TOKEN=0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63,METAVOLVE_WALLET=0xFE141943a93c184606F3060103D975662327063B" \
  --set-secrets="X_BEARER_TOKEN=x-bearer-token:latest" \
  --allow-unauthenticated

echo ""
echo "[4/4] Done."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "Service URL: ${SERVICE_URL}"
echo "Demo endpoint: POST ${SERVICE_URL}/demo (upload image)"
echo "Events: GET ${SERVICE_URL}/events"
echo "Stats: GET ${SERVICE_URL}/stats"
