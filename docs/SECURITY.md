# Security Model

SafeScroll treats page text, messages, OCR output and URLs as untrusted data. It does not execute scanned content.

Controls include input limits, schema validation, prompt-injection boundaries, rate limiting, SSRF-safe URL handling (the Web Risk provider receives only validated URLs), strict extension permissions, secret isolation, signed rule updates, non-root API containers and security-focused tests.

Detection results are probabilistic. A LOW RISK result never means guaranteed safe. Dangerous content may be missed and benign content can be flagged.
