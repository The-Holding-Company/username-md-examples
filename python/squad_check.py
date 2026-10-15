#!/usr/bin/env python3
"""Squad check: is <handle> on right now, and where do you join?

Resolution order:
  1. SRV  _playing._tcp.<handle>.username.md  -> live join target   (IN DEVELOPMENT)
  2. TXT  _presence.<handle>.username.md      -> structured presence (IN DEVELOPMENT)
  3. GET  /v1/users/<handle>/profile          -> roster + links      (live today)

The presence records are the gamer-tier surface (https://username.md/gamers.html)
and are IN DEVELOPMENT: until they are announced in https://username.md/llms.txt,
expect empty answers and the profile fallback. Write integrations exactly like
this — treat NXDOMAIN / empty answers as "not published", never as an error.

Usage:
    pip install -r requirements.txt
    python squad_check.py chris
"""
import sys

import dns.resolver
import requests

handle = (sys.argv[1:] or ["chris"])[0]
zone = f"{handle}.username.md"


def lookup(qname: str, rtype: str) -> list:
    """Resolve, treating 'no records' as an empty (not exceptional) answer."""
    try:
        return list(dns.resolver.resolve(qname, rtype))
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.resolver.LifetimeTimeout,
    ):
        return []


online = False

for srv in lookup(f"_playing._tcp.{zone}", "SRV"):
    online = True
    print(f"IN GAME — join {str(srv.target).rstrip('.')}:{srv.port}")

presence = {}
for rdata in lookup(f"_presence.{zone}", "TXT"):
    for raw in rdata.strings:
        text = raw.decode()
        if "=" in text:
            key, value = text.split("=", 1)
            presence[key] = value
if presence:
    online = online or presence.get("live") == "true"
    print(f"presence: {presence}")

if not online:
    # Presence not published (records are in development) — the profile API is
    # live today and always answers: who is /u/<handle>, and what do they play?
    print(f"{handle}: no live presence published — falling back to the profile API")
    resp = requests.get(
        f"https://username.md/v1/users/{handle}/profile",
        headers={"Accept": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()
    profile = resp.json()
    print(f"/u/{handle} — {profile.get('name') or handle}: {profile.get('tagline', '')}")
    for link in profile.get("links", []):
        print(f"  {link.get('label')}: {link.get('href')}")
