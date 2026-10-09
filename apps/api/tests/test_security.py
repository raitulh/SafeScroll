import os
os.environ['JWT_SECRET']='test-secret-at-least-32-bytes-long-123456'
from app.services.security import hash_password, verify_password, create_access_token, decode_token

def test_password_hash_roundtrip():
    hashed=hash_password('a-strong-password-123')
    assert hashed != 'a-strong-password-123'
    assert verify_password('a-strong-password-123',hashed)
    assert not verify_password('wrong-password-123',hashed)

def test_access_token():
    token=create_access_token(42)
    payload=decode_token(token,'access')
    assert payload['sub']=='42'

def test_password_minimum():
    import pytest
    with pytest.raises(ValueError): hash_password('too-short')
