# Deployment Runbook — Cloud Run + Firebase Hosting

> Pre-flight: confirm `gcloud auth list` shows the right account and `gcloud config get-value project` shows `the-golden-codex-1111`. Run `gcloud auth application-default login` for ADC if not already set.

**Submission deadline:** Mon 2026-05-18 04:59 AM PT. **Recommended deploy window: Sat 2026-05-16 afternoon.** Leaves Sunday for fixes.

---

## Stage 1 — Deploy the GCX Cocktail Bar (~10 min)

```bash
cd services/gcx-bar
./deploy.sh
```

This builds the container, pushes to GCR, and deploys to Cloud Run in `us-west1`. Defaults to STUB MODE (any `X-Payment` header passes) — set `GCX_BAR_FACILITATOR_URL` to wire a real facilitator post-launch.

**Smoke test after deploy:**

```bash
URL=$(gcloud run services describe gcx-bar --region us-west1 --format='value(status.url)')
echo "Bar at: $URL"
curl "$URL/health" | jq
curl "$URL/menu" | jq '.menu | length'                          # expect 10
curl -i "$URL/dose?cocktail=aeternum-sour" 2>&1 | grep "HTTP/"   # expect HTTP/2 402
curl "$URL/dose?cocktail=aeternum-sour" -H "X-Payment: stub" | jq '.cocktail, .name'
# expect: "aeternum-sour", "The Aeternum Sour"
```

Map custom domain (optional): `tuneup.golden-codex.com` → Cloud Run via Firebase Hosting domain mapping. Skip for submission; the Cloud Run URL is fine.

## Stage 2 — Deploy the Apprentice agent (~10 min)

```bash
cd agents/apprentice
# Edit deploy.sh if needed — ensure X402_NETWORK and OPERATOR_VAULT are set
./deploy.sh
```

**Required env-vars (set in Cloud Run console or via `gcloud run deploy --set-env-vars`):**

```
X_BEARER_TOKEN              <secret>   # from developer.twitter.com
ANTHROPIC_API_KEY           <secret>   # from console.anthropic.com
KITE_PASSPORT_JWT           <secret>   # from kpass login
OPERATOR_VAULT              <addr>     # from kpass agent info
X402_NETWORK                base
AEGIS_URL                   https://aegis-agent-172867820131.us-west1.run.app
REGISTER_API_URL            https://register-api-mrxpfmpeia-uw.a.run.app
METAVOLVE_WALLET            0xFE141943a93c184606F3060103D975662327063B
ARTISWA_USER_ID             <X user_id>
B1ANK_USER_ID               <X user_id>
GOLDEN_CODEX_USER_ID        <X user_id>
```

**Smoke test:**

```bash
URL=$(gcloud run services describe apprentice-operator --region us-west1 --format='value(status.url)')
curl "$URL/health" | jq
# Trigger one poll cycle manually
curl -X POST "$URL/poll" | jq
```

## Stage 3 — Deploy Maestra (~10 min)

```bash
cd agents/maestra
./deploy.sh
```

**Required env-vars (Maestra-specific overlays on top of Apprentice's env):**

```
ANTHROPIC_API_KEY                   <same as Apprentice>
KITE_PASSPORT_JWT                   <same>
OPERATOR_VAULT                      <Maestra's vault if different>
GCX_BAR_URL                         <Cloud Run URL from Stage 1>
COCKTAIL_SLUG                       aeternum-sour
MAESTRA_MANDATE_BUDGET_USD          250
MAESTRA_MANDATE_TIER                tier-1-gcx-certified
MAESTRA_MANDATE_DOMAIN              vision-training
MAESTRA_AUTONOMOUS_MODE             true
DEMO_PRICING_VERIFY                 0.01
DEMO_PRICING_COCKTAIL               0.10
DEMO_PRICING_LICENSE                1.00
DEMO_PRICING_ARTIST_SHARE           0.95
DEMO_PRICING_PLATFORM_FEE           0.05
REGISTER_API_URL                    https://register-api-mrxpfmpeia-uw.a.run.app
```

Note `MAESTRA_AUTONOMOUS_MODE=true` is the Buildathon default. Set to `false` to restore the call-the-collector path.

**Smoke test:**

```bash
URL=$(gcloud run services describe maestra-operator --region us-west1 --format='value(status.url)')
curl "$URL/health" | jq
curl -X POST "$URL/poll" | jq
```

## Stage 4 — Deploy the live status page to Firebase Hosting (~5 min)

The `docs/kite-live.html` page is self-contained — no build step. Push it to Firebase Hosting under `golden-codex.com/kite-live`.

```bash
# From the golden-codex-website directory (where firebase.json lives):
cp /mnt/c/Users/atmta/source/repos/golden-codex-kite-novel/docs/kite-live.html \
   /mnt/c/Users/atmta/source/repos/golden_codex_pipeline/golden-codex-website/public/kite-live.html

cd /mnt/c/Users/atmta/source/repos/golden_codex_pipeline/golden-codex-website
firebase deploy --only hosting:golden-codex --message "kite-live status page"
```

The page lives at `https://golden-codex.com/kite-live.html`.

**Optional:** edit the polling section at the bottom of `kite-live.html` to wire the real Cloud Run URLs:

```javascript
const APPRENTICE_URL = 'https://apprentice-operator-<hash>.us-west1.run.app';
const MAESTRA_URL = 'https://maestra-operator-<hash>.us-west1.run.app';
```

Uncomment the `setInterval` block. The page degrades gracefully if those endpoints are unreachable — it'll keep showing the demo-animation state.

## Stage 5 — End-to-end dry-run (~15 min)

With all three Cloud Run services up + the live page deployed:

1. Post a staged tweet to `@artiswagallery` (or your test handle) with an image.
2. `curl -X POST <apprentice URL>/poll` (manual trigger; Cloud Scheduler will fire too on its 60s cycle).
3. Watch Cloud Run logs for Apprentice → Maestra → gcx-bar → AO Registrar in sequence.
4. Open `golden-codex.com/kite-live` — confirm the ledger updates with real tx hashes.
5. Confirm Phase 3 AO Amendment lands by hitting `https://register-api-mrxpfmpeia-uw.a.run.app/provenance/GCX-AAt-07` and looking for the new `LicenseGranted` amendment in the chain.

If anything fails:
- Cloud Run logs: `gcloud run services logs read <service> --region us-west1 --limit 50`
- Anchor txs (always citable): `0x09deffc1…7623` + `0xa8c7f3fc…840886`

## Rollback

If Cloud Run deploy goes sideways:

```bash
# Rollback Cloud Run service to previous revision
gcloud run services update-traffic <service> --to-revisions <prev-revision>=100 --region us-west1
```

Firebase Hosting: previous version retained automatically; revert via console.

---

## Cost sanity check

Cloud Run + Firebase Hosting at expected demo traffic (~50 page views, ~10 demo cycles) costs well under $1 for the day. Real settlements at full pricing = $1.02 × demo runs. Budget $20 of Passport USDC for the full submission window (10–20 dry-run cycles). Tad's wallet (per the 2026-04-29 session) had 19.99 USDC.e at last check.

## Pre-deploy checklist

- [ ] `gcloud auth list` shows `atmtad@gmail.com` active
- [ ] `gcloud config get-value project` returns `the-golden-codex-1111`
- [ ] `kpass me` returns a valid Passport session (re-auth if needed — 2026-04-29 session expired)
- [ ] `kpass wallet balance` shows ≥ $5 USDC for dry-run cycles
- [ ] ANTHROPIC_API_KEY confirmed valid
- [ ] X_BEARER_TOKEN confirmed valid (test with curl)
- [ ] X_USER_IDs for @artiswagallery / @0x_b1ank / @Golden_Codex on hand
- [ ] Repo pushed (`git push origin main`)
