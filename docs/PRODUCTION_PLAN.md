# SafeScroll Production Release Plan

## Release candidate completed in this repository
- Auth: Argon2 password hashing, short-lived access JWTs, rotating refresh tokens, revocation.
- Small Mode: shipped hashed-character linear classifier artifact for local browser inference.
- Enhanced Mode: Ollama + Qwen3:1.7B with structured JSON output and prompt-injection boundary.
- Threat Intel: Google Web Risk adapter; disabled by default and only enabled in Enhanced URL scans.
- Signed rules: Ed25519 signing/verification tooling.
- Observability: Prometheus metrics and readiness checks.
- Security tests: auth, XSS-ish text handling, URL heuristics; browser E2E scaffold.
- Deployment: Docker hardened container and AWS Terraform baseline.
- OCR: build-time pinned worker/core/language assets; no runtime CDN dependency after `prepare:assets`.

## Still requiring operator-owned production actions
1. Create your production domain, OAuth/email provider, cloud account and secrets.
2. Generate/sign rule releases with your private operator key in a secret manager.
3. Train the small classifier on licensed public corpora and internal red-team examples; the shipped seed model is a bootstrap artifact, not a production accuracy claim.
4. Execute the UCI benchmark plus scam-specific holdout tests and calibrate thresholds on your operating data.
5. Configure Google Web Risk if your commercial deployment needs hosted URL reputation. Web Risk Lookup sends the queried URL to Google; Update API can keep local hashed lists for a more privacy-oriented architecture.
6. Complete Chrome Web Store listing, privacy disclosure, permission justification and human review. The extension uses `activeTab` + `scripting` to avoid broad permanent host access.
7. Configure staging/prod monitoring, WAF, backups, alert routing, remote state, secret manager and incident response.
