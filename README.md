# username.md — API examples

Runnable sample code for the [username.md](https://username.md) public API in
four languages. Every example runs against the live production API — no signup
needed for the read paths.

- **Developer guide:** https://username.md/developers.html
- **OpenAPI spec:** https://username.md/openapi.yaml ([browsable reference](https://username.md/api.html))
- **What username.md is:** one handle that resolves to your profile, your
  `did:web` document, your signed claims, and your ATProto/Bluesky identity —
  built for humans *and* AI agents.

## Languages

| Directory | Covers | Runtime |
|---|---|---|
| [`curl/`](curl/) | Every endpoint, copy-paste one-liners | curl |
| [`python/`](python/) | Profile fetch, signed-response verification, claims + domain verification | Python 3.10+ |
| [`javascript/`](javascript/) | Profile fetch, signed-response verification | Node 20+ (no deps) |
| [`go/`](go/) | Profile fetch, signed-response verification | Go 1.21+ (stdlib only) |

Each directory has its own README with setup and run instructions.

## The 30-second tour

```bash
# A handle's structured profile
curl -s -H 'accept: application/json' https://username.md/v1/users/chris/profile

# The same profile as Markdown, JSON-LD, or a signed JWS bundle
curl -s -H 'accept: text/markdown'        https://username.md/v1/users/chris/profile
curl -s -H 'accept: application/ld+json'  https://username.md/v1/users/chris/profile
curl -s -H 'accept: application/jose+json' https://username.md/v1/users/chris/profile

# The handle's did:web document
curl -s https://username.md/users/chris/.well-known/did.json

# Signed verifiable credentials ("claims")
curl -s https://username.md/v1/users/chris/claims

# Instructions for AI agents
curl -s https://username.md/users/chris/llms.txt
```

## Verifying signed responses

Every API response is signed with the platform's Ed25519 key using
[RFC 9421 HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
plus an [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530) `Content-Digest`.
Three response headers let you prove a payload really came from username.md
without trusting the transport:

```
Content-Digest:  sha-256=:<base64(sha256(body))>:
Signature-Input: sig1=("content-digest" "@authority");created=...;keyid="platform-ed25519";alg="ed25519"
Signature:       sig1=:<base64(ed25519 signature)>:
```

The covered components are `content-digest` (body integrity) and `@authority`
(the serving host), and the signature base is built per RFC 9421 §2.5:

```
"content-digest": sha-256=:...:
"@authority": username.md
"@signature-params": ("content-digest" "@authority");created=...;keyid="platform-ed25519";alg="ed25519"
```

The public verification key is published as a JWKS at
`https://username.md/.well-known/http-message-signatures-directory`
(kid `platform-ed25519`). Working verifiers:
[python/verify_signature.py](python/verify_signature.py) ·
[javascript/verify-signature.mjs](javascript/verify-signature.mjs) ·
[go/cmd/verify](go/cmd/verify/main.go).

## Authentication

Public reads need no credentials. Owner operations (PATCH profile, issue
claims, bind ATProto, DNS verification) take a Bearer API token issued when
you [claim a handle](https://username.md/claim.html) — regenerate it any time
in the [control panel](https://username.md/panel).

```bash
curl -s -X PATCH https://username.md/v1/users/YOURHANDLE/profile \
  -H "authorization: Bearer $USERNAME_MD_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"tagline": "hello from the API"}'
```

## License

MIT — see [LICENSE](LICENSE). The examples are yours to copy into your own
projects.
