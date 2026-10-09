#!/usr/bin/env python3
import argparse, base64, json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
p=argparse.ArgumentParser(); p.add_argument('--rules',required=True); p.add_argument('--private-key',required=True); p.add_argument('--out',required=True); args=p.parse_args()
data=Path(args.rules).read_bytes(); key=Ed25519PrivateKey.from_private_bytes(base64.b64decode(Path(args.private_key).read_text().strip())); sig=base64.b64encode(key.sign(data)).decode();
Path(args.out).write_text(json.dumps({'algorithm':'Ed25519','signature':sig,'payload_sha256':__import__('hashlib').sha256(data).hexdigest()},indent=2)+"\n")
print(args.out)
