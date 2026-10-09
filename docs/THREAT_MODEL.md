# Threat Model

Assets: user privacy, scan integrity, extension integrity, model/rule integrity, auth sessions, service availability.

Threats: malicious webpage content, prompt injection, Unicode spoofing, phishing URL tricks, XSS, SSRF, credential theft, token replay, rule tampering, dependency compromise, abusive scanning.

Mitigations are implemented in code and tested where practical. Remaining residual risk includes adversarial examples and incomplete threat intelligence.
