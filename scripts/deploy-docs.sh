#!/bin/bash
#
# Deploy the Konstrukt docs site to Cloudflare Pages.
#
# Publishes apps/konstrukt/docs/ as a static site. The custom domain
# design.thehoomanloop.com is attached once in the Cloudflare dashboard
# (see scripts/README-deploy.md). Requires CF_ACCOUNT_ID and CF_API_TOKEN
# (from the repo .env) plus a Cloudflare Pages project named konstrukt-docs.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CF_PROJECT_NAME="${KONSTRUKT_CF_PROJECT:-konstrukt-docs}"

echo "════════════════════════════════════════════════════════"
echo "  KONSTRUKT DOCS — DEPLOY"
echo "════════════════════════════════════════════════════════"

# Load repo-level .env if present (CF_ACCOUNT_ID / CF_API_TOKEN).
ENV_FILE="$PROJECT_DIR/../../.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

if [ -z "$CF_ACCOUNT_ID" ] || [ -z "$CF_API_TOKEN" ]; then
  echo "Error: CF_ACCOUNT_ID and CF_API_TOKEN must be set (see .env.example)."
  exit 1
fi

echo "Building Konstrukt (tokens + docs assets)..."
cd "$PROJECT_DIR"
npm run build
npm run check

echo "Publishing docs/ to Cloudflare Pages project '$CF_PROJECT_NAME'..."
CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID" CLOUDFLARE_API_TOKEN="$CF_API_TOKEN" \
  npx --yes wrangler pages deploy docs \
    --project-name="$CF_PROJECT_NAME" \
    --commit-dirty=true

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Live at https://design.thehoomanloop.com (after DNS)"
echo "  First-time setup: scripts/README-deploy.md"
echo "════════════════════════════════════════════════════════"
