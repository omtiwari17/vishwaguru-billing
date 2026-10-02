import base64
import hashlib
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet():
    """
    Returns a Fernet instance using an encryption key derived deterministically
    from settings.FIELD_ENCRYPTION_KEY or settings.SECRET_KEY.
    Produces a 32-byte URL-safe base64-encoded key.
    """
    raw_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not raw_key:
        raw_key = settings.SECRET_KEY
    # Hash raw key to 32 bytes and base64-encode for Fernet
    key_bytes = hashlib.sha256(raw_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


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

    f = _get_fernet()
    token = f.encrypt(val_str.encode('utf-8')).decode('utf-8')
    return f"enc:{token}"


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

    token = val_str[4:]
    try:
        f = _get_fernet()
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except (InvalidToken, Exception):
        # Fallback if key mismatch or corrupted
        return val_str


class EncryptedCharField(models.CharField):
    """
    A Django model CharField that transparently encrypts data at rest
    in the database and decrypts on retrieval.
    """
    description = "Field transparently encrypted at rest with Fernet (AES-128-CBC + HMAC-SHA256)"

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
