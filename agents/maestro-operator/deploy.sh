#!/bin/bash
set -e

PROJECT_ID="the-golden-codex-1111"
SERVICE_NAME="maestro-operator"
REGION="us-west1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
SA_NAME="maestro-operator-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Maestro Operator — Autonomous Freelance Art Collector ==="
echo "Cloud Run + Claude Sonnet + Aegis + x402 Kite + Firestore memory"
echo ""

# --- Service Account (least privilege) ---
echo "[1/5] Ensuring service account: ${SA_EMAIL}"
gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Maestro Operator (autonomous collector)" \
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

echo "  Permissions: Firestore user, Cloud Run invoker, Secret Manager accessor"

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
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},FIRESTORE_DB=golden-codex-database,AEGIS_URL=https://aegis-agent-172867820131.us-west1.run.app,X402_NETWORK=${X402_NETWORK:-kite},METAVOLVE_WALLET=0xFE141943a93c184606F3060103D975662327063B,ARTISWA_USER_ID=2019690975011172361,B1ANK_USER_ID=2019692766843006981,GOLDEN_CODEX_USER_ID=1995768015900807168" \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,X_BEARER_TOKEN=x-bearer-token:latest" \
  --no-allow-unauthenticated

# --- Cloud Scheduler (poll every 3 minutes — slower than CIL, more deliberate) ---
echo ""
echo "[4/5] Setting up Cloud Scheduler..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

gcloud scheduler jobs describe maestro-poll-cycle --location="${REGION}" --project="${PROJECT_ID}" 2>/dev/null && \
  gcloud scheduler jobs update http maestro-poll-cycle \
    --location="${REGION}" \
    --schedule="*/3 * * * *" \
    --uri="${SERVICE_URL}/poll" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}" 2>/dev/null || \
  gcloud scheduler jobs create http maestro-poll-cycle \
    --location="${REGION}" \
    --schedule="*/3 * * * *" \
    --uri="${SERVICE_URL}/poll" \
    --http-method=POST \
    --oidc-service-account-email="${SA_EMAIL}" \
    --project="${PROJECT_ID}"

echo ""
echo "[5/5] Verifying..."
echo "Service URL: ${SERVICE_URL}"
echo "Schedule: Every 3 minutes"
echo "Auth: Service account OIDC (no public access)"
echo ""
echo "=== Maestro Operator deployed ==="
echo "Maestro will begin curating autonomously."
echo "Collection: ${SERVICE_URL}/collection"
echo "Decisions: ${SERVICE_URL}/decisions"
echo "Daily budget: \$5.00 (resets at midnight UTC)"
