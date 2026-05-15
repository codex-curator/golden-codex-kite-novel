#!/bin/bash
# Deploy gcx-bar to Cloud Run
set -euo pipefail

PROJECT_ID="the-golden-codex-1111"
SERVICE_NAME="gcx-bar"
REGION="us-west1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Customize via env or override at runtime
PAY_TO="${GCX_BAR_PAY_TO:-0xFE141943a93c184606F3060103D975662327063B}"
NETWORK="${GCX_BAR_NETWORK:-eip155:8453}"
ASSET="${GCX_BAR_ASSET:-0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913}"
FACILITATOR="${GCX_BAR_FACILITATOR_URL:-}"
BASE_URL="${GCX_BAR_BASE_URL:-https://tuneup.golden-codex.com}"

echo "=== Deploying ${SERVICE_NAME} to ${PROJECT_ID} (${REGION}) ==="

gcloud builds submit --tag "${IMAGE}" --project "${PROJECT_ID}"

gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 60 \
    --concurrency 40 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars "GCX_BAR_PAY_TO=${PAY_TO},GCX_BAR_NETWORK=${NETWORK},GCX_BAR_ASSET=${ASSET},GCX_BAR_FACILITATOR_URL=${FACILITATOR},GCX_BAR_BASE_URL=${BASE_URL}" \
    --project "${PROJECT_ID}"

URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --project "${PROJECT_ID}" --format='value(status.url)')

echo ""
echo "=== Deployed ==="
echo "URL:   ${URL}"
echo "Menu:  ${URL}/menu"
echo "Order: ${URL}/dose?cocktail=aeternum-sour"
echo "Health: ${URL}/health"
echo ""
echo "Smoke test (expect 402):"
echo "  curl -i ${URL}/dose?cocktail=aeternum-sour"
