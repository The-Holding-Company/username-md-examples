// Fetch a username.md profile in each representation.
//
// Usage: go run ./cmd/profile <handle> [base_url]
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

func get(url, accept string) []byte {
	req, _ := http.NewRequest(http.MethodGet, url, nil)
	req.Header.Set("Accept", accept)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		panic(fmt.Sprintf("%s: %s", url, resp.Status))
	}
	return body
}

func main() {
	handle, base := "chris", "https://username.md"
	if len(os.Args) > 1 {
		handle = os.Args[1]
	}
	if len(os.Args) > 2 {
		base = os.Args[2]
	}
	url := fmt.Sprintf("%s/v1/users/%s/profile", base, handle)

	// Structured JSON — what an agent or integration usually wants.
	var profile struct {
		Handle  string `json:"handle"`
		Did     string `json:"did"`
		Name    string `json:"name"`
		Tagline string `json:"tagline"`
		Links   []struct {
			Label string `json:"label"`
			Href  string `json:"href"`
		} `json:"links"`
	}
	if err := json.Unmarshal(get(url, "application/json"), &profile); err != nil {
		panic(err)
	}
	fmt.Printf("handle : %s\ndid    : %s\nname   : %s\nlinks  : %d\n",
		profile.Handle, profile.Did, profile.Name, len(profile.Links))

	// schema.org/Person JSON-LD — for knowledge graphs.
	var jsonld map[string]any
	json.Unmarshal(get(url, "application/ld+json"), &jsonld)
	fmt.Printf("\nJSON-LD @type: %v\n", jsonld["@type"])

	// Markdown — terminal- and LLM-friendly.
	md := get(url, "text/markdown")
	if len(md) > 400 {
		md = md[:400]
	}
	fmt.Printf("\n--- markdown ---\n%s\n", md)
}
