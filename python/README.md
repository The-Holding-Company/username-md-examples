# Python examples

Python 3.10+.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python profile.py chris                 # fetch a profile (JSON / Markdown / JSON-LD)
.venv/bin/python verify_signature.py chris        # verify the RFC 9421 response signature
.venv/bin/python claims_and_domains.py chris      # read + verify the signed claim bundle
.venv/bin/python squad_check.py chris             # gamer presence: on now? where to join?
```

| File | What it shows |
|---|---|
| [`profile.py`](profile.py) | Content negotiation — one URL, four representations |
| [`verify_signature.py`](verify_signature.py) | Verify `Content-Digest` + Ed25519 `Signature` headers against the published JWKS |
| [`claims_and_domains.py`](claims_and_domains.py) | Fetch the claim bundle and verify each JWS against the handle's own public key; owner flow for DNS-TXT domain proof (needs `USERNAME_MD_TOKEN`) |
| [`squad_check.py`](squad_check.py) | Gamer presence: resolve `_playing` SRV / `_presence` TXT (**in development** — empty until announced in [llms.txt](https://username.md/llms.txt)), fall back to the live profile API |

Owner operations read the API token from the `USERNAME_MD_TOKEN` environment
variable — never hard-code it.
