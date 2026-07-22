#!/usr/bin/env python3
"""Fetch a username.md profile in each representation.

Usage: python profile.py <handle> [base_url]
"""
import json
import sys

import requests

BASE = sys.argv[2] if len(sys.argv) > 2 else "https://username.md"
handle = sys.argv[1] if len(sys.argv) > 1 else "chris"
url = f"{BASE}/v1/users/{handle}/profile"

# Structured JSON — what an agent or integration usually wants.
profile = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
profile.raise_for_status()
data = profile.json()
print(f"handle : {data['handle']}")
print(f"did    : {data['did']}")
print(f"name   : {data.get('name', '')}")
print(f"links  : {len(data.get('links', []))}")

# schema.org/Person JSON-LD — for knowledge graphs and SEO tooling.
jsonld = requests.get(url, headers={"Accept": "application/ld+json"}, timeout=10).json()
print("\nJSON-LD @type:", jsonld.get("@type"))

# Markdown — terminal- and LLM-friendly.
md = requests.get(url, headers={"Accept": "text/markdown"}, timeout=10).text
print("\n--- markdown ---")
print(md.strip()[:400])

# Signed JWS bundle — the whole profile as a verifiable artifact.
jws = requests.get(url, headers={"Accept": "application/jose+json"}, timeout=10).text
header = json.loads(__import__("base64").urlsafe_b64decode(jws.split(".")[0] + "=="))
print("\nJWS alg:", header.get("alg"), "| segments:", len(jws.split(".")))
