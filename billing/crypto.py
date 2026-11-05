import base64
import hashlib
import hmac
import os
from django.conf import settings
from django.db import models

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    Fernet = None
    InvalidToken = Exception


def _get_raw_key_bytes() -> bytes:
    raw_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not raw_key:
        raw_key = getattr(settings, 'SECRET_KEY', 'default-insecure-key-for-billing')
    return hashlib.sha256(raw_key.encode('utf-8')).digest()


def _get_fernet():
    """
    Returns a Fernet instance using an encryption key derived deterministically
    from settings.FIELD_ENCRYPTION_KEY or settings.SECRET_KEY.
    Produces a 32-byte URL-safe base64-encoded key.
    """
    key_bytes = _get_raw_key_bytes()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def _stdlib_encrypt(val_str: str) -> str:
    """
    Pure-Python standard-library authenticated stream cipher fallback when
    cryptography/Fernet is not installed.
    Uses HMAC-SHA256 in counter mode with 16-byte random IV and 16-byte HMAC verification tag.
    Zero external dependencies.
    """
    key_bytes = _get_raw_key_bytes()
    iv = os.urandom(16)
    data = val_str.encode('utf-8')
    keystream = bytearray()
    counter = 0
    while len(keystream) < len(data):
        keystream.extend(hmac.new(key_bytes, iv + counter.to_bytes(4, 'big'), hashlib.sha256).digest())
        counter += 1
    ciphertext = bytes(a ^ b for a, b in zip(data, keystream[:len(data)]))
    tag = hmac.new(key_bytes, iv + ciphertext, hashlib.sha256).digest()[:16]
    blob = iv + tag + ciphertext
    token = base64.urlsafe_b64encode(blob).decode('utf-8')
    return f"enc:std:{token}"


def _stdlib_decrypt(token_str: str) -> str:
    """
    Decrypts a standard-library authenticated token.
    """
    key_bytes = _get_raw_key_bytes()
    try:
        blob = base64.urlsafe_b64decode(token_str.encode('utf-8'))
        if len(blob) < 32:
            return token_str
        iv = blob[:16]
        tag = blob[16:32]
        ciphertext = blob[32:]
        expected_tag = hmac.new(key_bytes, iv + ciphertext, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(tag, expected_tag):
            return token_str
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(ciphertext):
            keystream.extend(hmac.new(key_bytes, iv + counter.to_bytes(4, 'big'), hashlib.sha256).digest())
            counter += 1
        data = bytes(a ^ b for a, b in zip(ciphertext, keystream[:len(ciphertext)]))
        return data.decode('utf-8')
    except Exception:
        return token_str


def encrypt_value(value: str) -> str:
    """
    Encrypts a plaintext string and prefixes it with 'enc:'
    so it can be reliably identified as encrypted ciphertext.
    """
    if value is None:
        return None
    val_str = str(value).strip()
    if not val_str:
        return ''
    if val_str.startswith('enc:'):
        return val_str  # Avoid double-encryption

    if HAS_CRYPTOGRAPHY and Fernet is not None:
        f = _get_fernet()
        token = f.encrypt(val_str.encode('utf-8')).decode('utf-8')
        return f"enc:{token}"
    else:
        return _stdlib_encrypt(val_str)


def decrypt_value(value: str) -> str:
    """
    Decrypts an 'enc:' prefixed ciphertext string.
    If the value is not prefixed with 'enc:', returns it as-is
    for backward compatibility with legacy unencrypted data.
    """
    if value is None:
        return None
    val_str = str(value)
    if not val_str.startswith('enc:'):
        return val_str  # Legacy unencrypted plaintext

    if val_str.startswith('enc:std:'):
        return _stdlib_decrypt(val_str[8:])

    token = val_str[4:]
    if HAS_CRYPTOGRAPHY and Fernet is not None:
        try:
            f = _get_fernet()
            return f.decrypt(token.encode('utf-8')).decode('utf-8')
        except (InvalidToken, Exception):
            return val_str
    else:
        return val_str


class EncryptedCharField(models.CharField):
    """
    A Django model CharField that transparently encrypts data at rest
    in the database and decrypts on retrieval.
    """
    description = "Field transparently encrypted at rest with Fernet (or stdlib HMAC fallback)"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_value(value)

    def to_python(self, value):
        if value is None:
            return value
        return decrypt_value(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == '':
            return value
        return encrypt_value(value)
