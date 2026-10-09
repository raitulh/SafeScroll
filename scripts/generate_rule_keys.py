#!/usr/bin/env python3
from base64 import b64encode
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
key=Ed25519PrivateKey.generate(); pub=key.public_key()
out=Path('secrets/rules'); out.mkdir(parents=True,exist_ok=True)
(out/'private_key.b64').write_text(b64encode(key.private_bytes_raw()).decode()+"\n")
(out/'public_key.b64').write_text(b64encode(pub.public_bytes_raw()).decode()+"\n")
print('Created test/operator keys under secrets/rules. Never commit the private key.')
