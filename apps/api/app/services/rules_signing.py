from base64 import b64decode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from app.config import settings

class SignatureError(ValueError):
    pass

def verify_signed_rules(payload: bytes, signature_b64: str) -> bool:
    if not settings.rules_signing_public_key_b64:
        if settings.rules_require_signature:
            raise SignatureError("Rules signing public key is not configured.")
        return False
    try:
        key = Ed25519PublicKey.from_public_bytes(b64decode(settings.rules_signing_public_key_b64))
        key.verify(b64decode(signature_b64), payload)
        return True
    except (ValueError, InvalidSignature) as exc:
        raise SignatureError("Rule signature verification failed.") from exc
