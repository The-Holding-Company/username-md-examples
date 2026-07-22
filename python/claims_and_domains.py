#!/usr/bin/env python3
"""Read a handle's signed claim bundle and verify each credential's JWS
against the handle's own published Ed25519 key. With USERNAME_MD_TOKEN set,
also demonstrates the DNS-TXT domain-ownership flow (owner only).

Usage: python claims_and_domains.py <handle> [base_url]
"""
import base64
import json
import os
import sys

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

BASE = sys.argv[2] if len(sys.argv) > 2 else "https://username.md"
handle = sys.argv[1] if len(sys.argv) > 1 else "chris"


def b64url(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


bundle = requests.get(f"{BASE}/v1/users/{handle}/claims", timeout=10).json()
pub = Ed25519PublicKey.from_public_bytes(b64url(bundle["public_jwk"]["x"]))
print(f"{handle}: did={bundle['did']} claims={len(bundle['claims'])}")

for claim in bundle["claims"]:
    signing_input, sig = claim["jws"].rsplit(".", 1)
    try:
        pub.verify(b64url(sig), signing_input.encode())
        verdict = "VALID"
    except InvalidSignature:
        verdict = "INVALID"
    ctype = claim["type"]
    subject = json.dumps(claim["credential"].get("credentialSubject", {}))[:60]
    print(f"  [{verdict}] {ctype:<20} {subject}")

# --- Owner flow: prove you control a domain (requires your API token) -------
token = os.environ.get("USERNAME_MD_TOKEN")
domain = os.environ.get("USERNAME_MD_DOMAIN")
if token and domain:
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    challenge = requests.post(
        f"{BASE}/v1/users/{handle}/verifications/dns-txt",
        headers=auth, json={"domain": domain}, timeout=10,
    ).json()
    print(f"\nPublish this TXT record, then re-run with the record live:")
    print(f"  {challenge['record_name']}  TXT  \"{challenge['record_value']}\"")
    check = requests.post(
        f"{BASE}/v1/users/{handle}/verifications/dns-txt/check",
        headers=auth, json={"domain": domain}, timeout=15,
    )
    print(f"check: {check.status_code} {check.json()}")
else:
    print("\n(set USERNAME_MD_TOKEN and USERNAME_MD_DOMAIN to try the domain-proof flow)")
