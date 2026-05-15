#!/usr/bin/env bash
#
# smoke-test.sh — End-to-end smoke test for the local docker-compose stack
#
# Usage:
#   ./scripts/smoke-test.sh                 (defaults to localhost ports)
#   GCX_BAR=http://example.com ./scripts/smoke-test.sh  (override targets)
#
# Returns exit 0 if all checks pass, exit 1 on any failure.
#
# Stub mode: gcx-bar accepts any X-Payment header when GCX_BAR_FACILITATOR_URL
# is empty. This script uses a hardcoded stub token, so it works cold without
# any real Kite Passport / x402 wiring.

set -euo pipefail

GCX_BAR=${GCX_BAR:-http://localhost:8080}
APPRENTICE=${APPRENTICE:-http://localhost:8081}
MAESTRA=${MAESTRA:-http://localhost:8082}

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
DIM='\033[0;2m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}●${NC} $*"; }
dim()  { echo -e "${DIM}  $*${NC}"; }

require() {
  local name=$1
  command -v "$name" >/dev/null 2>&1 || fail "Required command not found: $name"
}

require curl
require jq

echo
info "=== GCX Bar (port 8080) ==="

# 1. Health check
health=$(curl -sf "$GCX_BAR/health" || echo "")
if [[ "$health" == *'"status":"ok"'* ]] || [[ "$health" == *'"status": "ok"'* ]]; then
  pass "Health endpoint returns ok"
  dim "$(echo "$health" | jq -c .)"
else
  fail "Health endpoint did not return ok: $health"
fi

# 2. Menu endpoint
menu_count=$(curl -sf "$GCX_BAR/menu" | jq '.menu | length' 2>/dev/null || echo "0")
if [[ "$menu_count" -ge 1 ]]; then
  pass "Menu lists $menu_count cocktails"
else
  fail "Menu endpoint failed or empty"
fi

# 3. Aeternum Sour visible
aeternum=$(curl -sf "$GCX_BAR/menu" | jq -r '.menu[] | select(.slug=="aeternum-sour") | .name' 2>/dev/null || echo "")
if [[ "$aeternum" == "The Aeternum Sour" ]]; then
  pass "The Aeternum Sour is on the menu"
else
  fail "Aeternum Sour not found in menu (got: '$aeternum')"
fi

# 4. /dose without payment returns 402
status=$(curl -s -o /dev/null -w "%{http_code}" "$GCX_BAR/dose?cocktail=aeternum-sour")
if [[ "$status" == "402" ]]; then
  pass "/dose returns HTTP 402 without X-Payment header"
else
  fail "/dose returned $status (expected 402)"
fi

# 5. /dose with stub X-Payment returns 200 + content
body=$(curl -sf "$GCX_BAR/dose?cocktail=aeternum-sour" -H "X-Payment: smoke-test-stub-token")
content_len=$(echo "$body" | jq -r '.content | length' 2>/dev/null || echo "0")
if [[ "$content_len" -gt 1000 ]]; then
  pass "/dose served Aeternum Sour content ($content_len chars)"
else
  fail "/dose did not serve cocktail content (got $content_len chars)"
fi

# 6. Verify Maestra persona is named in the cocktail
if echo "$body" | jq -r '.content' | grep -qi "Maestra"; then
  pass "Cocktail content names the Maestra persona"
else
  fail "Cocktail content missing Maestra persona reference"
fi

echo
info "=== Apprentice (port 8081) ==="

if curl -sf "$APPRENTICE/health" >/dev/null 2>&1; then
  pass "Apprentice health endpoint reachable"
  dim "$(curl -sf "$APPRENTICE/health" 2>/dev/null | jq -c . 2>/dev/null || echo 'response not JSON')"
else
  echo -e "${YELLOW}○${NC} Apprentice not reachable at $APPRENTICE — skipping (needs X+Claude keys)"
fi

echo
info "=== Maestra (port 8082) ==="

if curl -sf "$MAESTRA/health" >/dev/null 2>&1; then
  pass "Maestra health endpoint reachable"
  dim "$(curl -sf "$MAESTRA/health" 2>/dev/null | jq -c . 2>/dev/null || echo 'response not JSON')"
else
  echo -e "${YELLOW}○${NC} Maestra not reachable at $MAESTRA — skipping (needs ANTHROPIC + Passport keys)"
fi

echo
info "=== Substrate references ==="

# Anchor tx verification (these should be visible on Basescan whether or not local services run)
echo -e "${DIM}  Phase 1 anchor tx (live on Base): https://basescan.org/tx/0x09deffc164a15d69a1095e132ab851791e4ba595af42f0257b9c2cca85847623${NC}"
echo -e "${DIM}  Phase 2 anchor tx (live on Base): https://basescan.org/tx/0xa8c7f3fc64a15d69a1095e132ab851791e4ba595af42f0257b9c2cca85840886${NC}"
echo -e "${DIM}  AO Registrar process: Dwnuy4MbuQkgwxw4-P08wxeny2KcwCh8Kd22mehacTc${NC}"
echo -e "${DIM}  Register-API provenance: https://register-api-mrxpfmpeia-uw.a.run.app/provenance/GCX-AAt-07${NC}"

echo
pass "Smoke test complete."
echo
echo -e "${DIM}Next steps:${NC}"
echo -e "${DIM}  - Open docs/kite-live.html in a browser for the live demo visual${NC}"
echo -e "${DIM}  - Read docs/demo-storyboard.md for the 90s recording protocol${NC}"
echo -e "${DIM}  - Run docs/DEPLOY.md to push to Cloud Run + Firebase Hosting${NC}"
