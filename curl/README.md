# curl examples

Copy-paste one-liners for every public endpoint. Full reference:
[openapi.yaml](https://username.md/openapi.yaml) ·
[browsable API reference](https://username.md/api.html).

## Public reads (no auth)

```bash
H=chris   # any handle

# Profile — content-negotiated. Default is HTML; pick your representation:
curl -s -H 'accept: application/json'     https://username.md/v1/users/$H/profile
curl -s -H 'accept: application/ld+json'  https://username.md/v1/users/$H/profile   # schema.org/Person
curl -s -H 'accept: text/markdown'        https://username.md/v1/users/$H/profile
curl -s -H 'accept: application/jose+json' https://username.md/v1/users/$H/profile  # signed JWS bundle

# In a browser? Query alias beats the Accept header:
#   https://username.md/v1/users/chris/profile?accept=json
#   https://username.md/v1/users/chris/profile?theme=terminal   (theme preview)

# Theme / accent preferences
curl -s https://username.md/v1/users/$H/preferences

# Signed claim bundle (DID + public key + verifiable credentials)
curl -s https://username.md/v1/users/$H/claims

# did:web document
curl -s https://username.md/users/$H/.well-known/did.json

# ATProto / Bluesky binding status
curl -s https://username.md/v1/users/$H/atproto

# ATProto DID resolution (what Bluesky queries via <handle>.username.md)
curl -s https://username.md/users/$H/.well-known/atproto-did

# Instructions for AI agents
curl -s https://username.md/users/$H/llms.txt

# Platform response-signing keys (JWKS, RFC 9421)
curl -s https://username.md/.well-known/http-message-signatures-directory
```

## Gamer presence (in development)

Presence publishes as DNS SRV/TXT under the handle — the gamer-tier surface
described at [username.md/gamers.html](https://username.md/gamers.html). These
records are **in development**: until they're announced in
[llms.txt](https://username.md/llms.txt), lookups return empty answers. Treat
"no records" as *not published* (never an error) and fall back to the profile
API, which is live today.

```bash
H=chris

# In game right now? SRV answers with the join target
dig +short SRV _playing._tcp.$H.username.md

# Structured presence: live=, game=, join=, party=, next=
dig +short TXT _presence.$H.username.md

# Fallback that always answers: who is /u/$H, and what do they play?
curl -s -H 'accept: application/json' https://username.md/v1/users/$H/profile
```

Runnable versions with the fallback chain:
[python/squad_check.py](../python/squad_check.py) ·
[javascript/squad-check.mjs](../javascript/squad-check.mjs).

## Inspect the response signature

```bash
curl -sI -H 'accept: application/json' https://username.md/v1/users/chris/profile \
  | grep -iE 'content-digest|signature'
```

See the [python](../python/), [javascript](../javascript/), and [go](../go/)
examples for full cryptographic verification.

## Owner operations (Bearer token)

Your API token is issued when you [claim a handle](https://username.md/claim.html)
and can be regenerated in the [control panel](https://username.md/panel).

```bash
export USERNAME_MD_TOKEN='...'   # keep out of shell history: read from a secret store
H=yourhandle

# Update profile fields (partial — omitted fields unchanged)
curl -s -X PATCH https://username.md/v1/users/$H/profile \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"name":"Your Name","tagline":"builder","links":[{"label":"GitHub","href":"https://github.com/you"}]}'

# Set your default theme + accent
curl -s -X PUT https://username.md/v1/users/$H/preferences \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"theme":"terminal","accent":"#7ee787"}'

# Issue a signed claim
curl -s -X POST https://username.md/v1/users/$H/claims \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"type":"hasGitHub","value":"your-github-login"}'

# Prove you own a domain: get a TXT challenge, publish it, then check.
curl -s -X POST https://username.md/v1/users/$H/verifications/dns-txt \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"domain":"yourdomain.com"}'
# → {"domain":"yourdomain.com","record_name":"_did-web-verify.yourdomain.com","record_value":"<hex>"}
# Publish that TXT record at your DNS provider, wait for propagation, then:
curl -s -X POST https://username.md/v1/users/$H/verifications/dns-txt/check \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"domain":"yourdomain.com"}'

# Bind your Bluesky identity → @yourhandle.username.md
curl -s -X PUT https://username.md/v1/users/$H/atproto \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"did":"did:plc:your24charplcidentifier"}'
```
