# Signed rule updates

`rules.json` is the canonical rules payload. Production updates must be signed with Ed25519 by an operator key and verified before installation.

Generate an operator keypair:

```bash
python scripts/generate_rule_keys.py
```

Sign:

```bash
python scripts/sign_rules.py --rules packages/rules/rules.json --private-key secrets/rules/private_key.b64 --out packages/rules/rules.sig.json
```

The private key is never shipped to the extension or API container. CI should store it in a secret manager.
