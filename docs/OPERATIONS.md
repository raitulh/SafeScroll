# Operations runbook

Monitor `/api/v1/health`, `/api/v1/ready`, and `/metrics`. Alert on readiness degradation, elevated 5xx, scan latency, Redis errors, database connection exhaustion, and model timeout rates.

Before production: enable managed database backups, test restore, rotate JWT/rule keys, store secrets in a cloud secret manager, configure WAF/HTTPS, and run staging migrations before production migrations.
