# SafeScroll Architecture

## Principles

- Local-first by default.
- Deterministic security signals before generative AI.
- AI assists classification/explanation but does not become an unconditional trust oracle.
- Explainable evidence for every high-risk result.
- Minimize sensitive data collection.
- Graceful fallback when cloud services or models are unavailable.

## Scan pipeline

```text
Input -> Normalize -> Signals -> URL Intelligence -> Optional AI -> Risk Fusion -> Explanation -> Action
```

## Extension boundaries

Content scripts read only the user-requested page/selection. The background service worker coordinates analysis and API calls. UI renders sanitized plain text, never raw HTML from scanned content.

## Backend boundaries

FastAPI is an optional enhanced intelligence path. It validates payloads, caps input sizes, runs the same category semantics as the client engine, optionally calls Ollama, and emits minimum metadata.

## Future production hardening

- Signed rule bundle updates.
- Model version pinning and rollback.
- Threat-intelligence provider abstraction.
- Sentry release health.
- OpenTelemetry traces.
- KMS-managed secrets in hosted environments.
- External security review / penetration test.
