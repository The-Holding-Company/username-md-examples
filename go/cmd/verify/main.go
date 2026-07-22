// Verify a username.md API response signature (RFC 9421 + RFC 9530).
//
// Usage: go run ./cmd/verify <handle> [base_url]
package main

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
)

func main() {
	handle, base := "chris", "https://username.md"
	if len(os.Args) > 1 {
		handle = os.Args[1]
	}
	if len(os.Args) > 2 {
		base = os.Args[2]
	}
	u, _ := url.Parse(base)
	host := u.Host

	// 1. Fetch the platform verification key (kid: platform-ed25519).
	resp, err := http.Get(base + "/.well-known/http-message-signatures-directory")
	if err != nil {
		panic(err)
	}
	var jwks struct {
		Keys []struct {
			Kid string `json:"kid"`
			X   string `json:"x"`
		} `json:"keys"`
	}
	json.NewDecoder(resp.Body).Decode(&jwks)
	resp.Body.Close()
	var pub ed25519.PublicKey
	for _, k := range jwks.Keys {
		if k.Kid == "platform-ed25519" {
			raw, err := base64.RawURLEncoding.DecodeString(k.X)
			if err != nil {
				panic(err)
			}
			pub = ed25519.PublicKey(raw)
		}
	}
	if pub == nil {
		panic("platform-ed25519 key not found in JWKS")
	}

	// 2. Fetch any API response.
	req, _ := http.NewRequest(http.MethodGet, fmt.Sprintf("%s/v1/users/%s/profile", base, handle), nil)
	req.Header.Set("Accept", "application/json")
	resp, err = http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	body, _ := io.ReadAll(resp.Body)
	resp.Body.Close()

	// 3. Check the body digest (RFC 9530).
	digest := resp.Header.Get("Content-Digest")
	sum := sha256.Sum256(body)
	expected := "sha-256=:" + base64.StdEncoding.EncodeToString(sum[:]) + ":"
	if digest != expected {
		panic("Content-Digest does not match body")
	}

	// 4. Rebuild the RFC 9421 §2.5 signature base and verify the signature.
	params := strings.TrimPrefix(resp.Header.Get("Signature-Input"), "sig1=")
	sigHeader := resp.Header.Get("Signature")
	sig, err := base64.StdEncoding.DecodeString(strings.TrimSuffix(strings.TrimPrefix(sigHeader, "sig1=:"), ":"))
	if err != nil {
		panic(err)
	}
	sigBase := fmt.Sprintf("%q: %s\n%q: %s\n%q: %s",
		"content-digest", digest, "@authority", host, "@signature-params", params)
	if !ed25519.Verify(pub, []byte(sigBase), sig) {
		panic("signature verification FAILED")
	}
	fmt.Printf("verified: response for %q signed by %s\n", handle, host)
}
