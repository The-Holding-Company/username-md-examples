#!/usr/bin/env python3
"""Verify a username.md API response signature (RFC 9421 + RFC 9530).

Every response carries:
    Content-Digest:  sha-256=:<b64(sha256(body))>:
    Signature-Input: sig1=("content-digest" "@authority");created=...;keyid="platform-ed25519";alg="ed25519"
    Signature:       sig1=:<b64(ed25519 signature)>:

The verification key is a JWKS at /.well-known/http-message-signatures-directory.

Usage: python verify_signature.py <handle> [base_url]
"""
import base64
import hashlib
import sys

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

BASE = sys.argv[2] if len(sys.argv) > 2 else "https://username.md"
handle = sys.argv[1] if len(sys.argv) > 1 else "chris"
host = BASE.split("://", 1)[1].split("/", 1)[0]

# 1. Fetch the platform verification key (kid: platform-ed25519).
jwks = requests.get(f"{BASE}/.well-known/http-message-signatures-directory", timeout=10).json()
jwk = next(k for k in jwks["keys"] if k.get("kid") == "platform-ed25519")
pub = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(jwk["x"] + "=="))

# 2. Fetch any API response.
resp = requests.get(
    f"{BASE}/v1/users/{handle}/profile", headers={"Accept": "application/json"}, timeout=10
)
resp.raise_for_status()

# 3. Check the body digest (RFC 9530).
digest = resp.headers["Content-Digest"]
expected = "sha-256=:" + base64.b64encode(hashlib.sha256(resp.content).digest()).decode() + ":"
assert digest == expected, "Content-Digest does not match body"

# 4. Rebuild the RFC 9421 §2.5 signature base and verify the Ed25519 signature.
params = resp.headers["Signature-Input"].removeprefix("sig1=")
sig = base64.b64decode(resp.headers["Signature"][len("sig1=:"):-1])
base = (
    f'"content-digest": {digest}\n'
    f'"@authority": {host}\n'
    f'"@signature-params": {params}'
).encode("ascii")
pub.verify(sig, base)  # raises InvalidSignature if forged

print(f"verified: response for {handle!r} signed by {host}")
