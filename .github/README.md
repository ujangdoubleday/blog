# GitHub Actions Setup

This workflow automatically builds and deploys to IPFS (Pinata) and Cloudflare.

## Required Secrets

Add these secrets in **Settings → Secrets and variables → Actions**:

### Pinata (Required)

- `PINATA_API_KEY`
- `PINATA_SECRET_API_KEY`
- `PINATA_JWT`

### Cloudflare (Optional)

- `CLOUDFLARE` - Set to `true` or `false`. Default: `false`
- `CLOUDFLARE_EMAIL`
- `CLOUDFLARE_API_KEY`
- `CLOUDFLARE_ZONE_ID`
- `CLOUDFLARE_HOSTNAME`

## How It Works

1. Push to `main` triggers the workflow
2. Runs `./build.sh` and `./deploy.sh`
3. Deploys to Pinata IPFS
4. Updates Cloudflare DNSLink (if enabled)
5. Creates PR for snapshot changes
6. Auto-merges PR with squash commit
