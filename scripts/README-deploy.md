# Deploying the Konstrukt docs

The docs site (`apps/konstrukt/docs/`) is a self-contained static site. It is
published to Cloudflare Pages and served at **design.thehoomanloop.com**.

## One-time setup

1. **Create the Pages project** (Cloudflare dashboard or CLI):
   - Name: `konstrukt-docs`
   - Build command: _none_ (the assets are pre-built by `npm run build`)
   - Output directory: `docs`

2. **Add the custom domain** in the project's *Custom domains* tab:
   - `design.thehoomanloop.com`
   - Cloudflare adds the required `CNAME` automatically when the apex domain is
     already on Cloudflare (as `thehoomanloop.com` is).

3. **Credentials**: ensure the repo `.env` has `CF_ACCOUNT_ID` and
   `CF_API_TOKEN` with Pages edit permission (same token used by the main site
   deploy).

## Routine deploy

```bash
cd apps/konstrukt
bash scripts/deploy-docs.sh
```

The script rebuilds tokens, runs the parity check, copies the generated assets
into `docs/assets/`, copies `llms.txt` and `llms-full.txt` to the docs root, and
publishes `docs/` with `wrangler pages deploy`.

## Notes

- `docs/assets/` is generated (gitignored). The deploy always rebuilds it, so a
  fresh clone deploys correctly.
- The docs dogfood Konstrukt: they load `assets/konstrukt.css`,
  `assets/base.css`, and `assets/theme.js`, and the token reference renders live
  from `assets/tokens.json`.
