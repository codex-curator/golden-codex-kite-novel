#!/bin/bash
set -e

PROJECT_ID="the-golden-codex-1111"
SERVICE_NAME="apprentice-operator"
REGION="us-west1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
SA_NAME="apprentice-operator-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Apprentice Operator — Autonomous AI Training Data Buyer ==="
echo "Cloud Run + Claude Sonnet + Aegis + x402 Kite + Firestore memory"
echo ""

# --- Service Account (least privilege) ---
echo "[1/5] Ensuring service account: ${SA_EMAIL}"
gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Apprentice Operator (autonomous buyer)" \
    --project="${PROJECT_ID}"

# Firestore read/write (its memory + decision logs)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user" --quiet 2>/dev/null

# Cloud Run invoker (call Aegis, Atlas for verification)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" --quiet 2>/dev/null

# Secret Manager read (API keys)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" --quiet 2>/dev/null

echo "  Permissions: Firestore user, Cloud Run invoker, Secret Manager accessor"
echo "  NO admin, NO delete, NO deploy, NO billing, NO GCS write"

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
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},FIRESTORE_DB=golden-codex-database,AEGIS_URL=https://aegis-agent-172867820131.us-west1.run.app,KITE_FACILITATOR_URL=https://facilitator.pieverse.io,KITE_SETTLEMENT_TOKEN=0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63,METAVOLVE_WALLET=0xFE141943a93c184606F3060103D975662327063B" \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,X_BEARER_TOKEN=x-bearer-token:latest" \
  --no-allow-unauthenticated

# --- Cloud Scheduler (poll every 90 seconds) ---
echo ""
echo "[4/5] Setting up Cloud Scheduler..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

gcloud scheduler jobs describe apprentice-poll-cycle --location="${REGION}" --project="${PROJECT_ID}" 2>/dev/null && \
  gcloud scheduler jobs update http apprentice-poll-cycle \
    --location="${REGION}" \
    --schedule="*/2 * * * *" \
    --uri="${SERVICE_URL}/poll" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud scheduler jobs create http apprentice-poll-cycle \
    --location="${REGION}" \
    --schedule="*/2 * * * *" \
    --uri="${SERVICE_URL}/poll" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}"

echo ""
echo "[5/5] Verifying..."
echo "Service URL: ${SERVICE_URL}"
echo "Schedule: Every 2 minutes"
echo "Auth: Service account OIDC (no public access)"
echo ""
echo "=== Apprentice Operator deployed ==="
echo "It will begin monitoring X and licensing autonomously."
echo "Monitor: ${SERVICE_URL}/session"
echo "Decisions: ${SERVICE_URL}/decisions"
echo "Daily budget: \$10.00 (resets at midnight UTC)"
