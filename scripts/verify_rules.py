#!/usr/bin/env python3
import argparse,base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
p=argparse.ArgumentParser(); p.add_argument('--rules',required=True); p.add_argument('--signature',required=True); p.add_argument('--public-key',required=True); args=p.parse_args()
data=Path(args.rules).read_bytes(); meta=json.loads(Path(args.signature).read_text()); Ed25519PublicKey.from_public_bytes(base64.b64decode(Path(args.public_key).read_text().strip())).verify(base64.b64decode(meta['signature']),data); assert meta['payload_sha256']==hashlib.sha256(data).hexdigest(); print('VALID')
