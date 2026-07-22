# Go examples

Go 1.21+ — standard library only.

```bash
go run ./cmd/profile chris     # fetch a profile (JSON / Markdown / JSON-LD)
go run ./cmd/verify chris      # verify the RFC 9421 response signature
```

| Program | What it shows |
|---|---|
| [`cmd/profile`](cmd/profile/main.go) | Content negotiation — one URL, four representations |
| [`cmd/verify`](cmd/verify/main.go) | Verify `Content-Digest` + Ed25519 `Signature` headers against the published JWKS |

For owner operations (PATCH profile, claims, ATProto bind) send a normal
`http.Request` with `Authorization: Bearer <token>` (read the token from the
`USERNAME_MD_TOKEN` env var) — see the [curl examples](../curl/) for every
endpoint and payload shape.
