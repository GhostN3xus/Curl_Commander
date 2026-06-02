# CurlCommander

Terminal tool for building HTTP requests visually and generating curl commands.
Two modes from one entrypoint: `curlcmd`.

---

## 1. Installation

**Unix / macOS / WSL:**
```bash
bash install.sh
```

**Windows (PowerShell):**
```powershell
pip install -e ".[dev]"
```

Requires Python 3.11+.

---

## 2. CLI Mode — Flags & Examples

### Direct execution with flags

```bash
# Simple GET
curlcmd https://httpbin.org/get

# POST JSON
curlcmd -X POST --json '{"name":"ada"}' https://httpbin.org/post

# Bearer auth + custom header
curlcmd -X GET --auth-bearer mytoken -H "Accept: application/json" https://api.example.com/me

# Form body
curlcmd -X POST --form "user=ada&pass=secret" https://httpbin.org/post

# Read body from file
curlcmd -X POST --body-file payload.json https://api.example.com/upload

# API-key auth
curlcmd --auth-apikey "X-API-Key: abc123" https://api.example.com/data

# Generate curl without sending
curlcmd -X POST --json '{"id":1}' --curl-only https://api.example.com/users

# With query params
curlcmd -p "page=1" -p "limit=20" https://api.example.com/items

# Proxy, retry, HTTP/2, compression
curlcmd --proxy http://localhost:8080 --retry 3 --retry-delay 2 --http2 --compressed https://httpbin.org/get

# Save response body to a file
curlcmd --output response.txt https://httpbin.org/get

# Load environment variables from .env and use {{API_URL}} substitution
curlcmd --env-file .env -H "Authorization: Bearer {{API_TOKEN}}" {{API_URL}}

# Disable SSL verification + no redirect
curlcmd --no-verify --no-redirect https://self-signed.example.com/
```

### Interactive wizard (no flags)

```bash
curlcmd
```

Prompts for method, URL, headers, params, body, auth, and options step by step.

### History subcommands

```bash
curlcmd history             # list last 30 requests
curlcmd replay 5            # replay history entry #5
curlcmd curl 5              # print curl command for entry #5
curlcmd delete-history 5    # delete history entry #5
curlcmd export-history -o history.json  # export history to JSON file
curlcmd clear-history       # delete all history
```

### All flags

| Flag | Description |
|------|-------------|
| `-X, --method` | HTTP method (default: GET) |
| `-H, --header` | Header as `"Key: Value"` (repeatable) |
| `-p, --param` | Query param as `"key=value"` (repeatable) |
| `-b, --body` | Raw body string |
| `--body-file PATH` | Read body from file |
| `--json JSON` | JSON body (auto sets Content-Type) |
| `--form DATA` | Form-urlencoded body |
| `--auth-bearer TOKEN` | Bearer token |
| `--auth-basic USER:PASS` | Basic auth |
| `--auth-apikey 'H: V'` | API key in custom header |
| `--proxy URL` | Proxy URL for the request |
| `--retry N` | Retry on network errors up to N times |
| `--retry-delay SECS` | Delay between retry attempts |
| `--compressed` | Request compressed response |
| `--http2` | Use HTTP/2 if supported |
| `--output PATH` | Save response body to a file |
| `--pretty` | Pretty-print response body when possible |
| `--env-file PATH` | Load variables from a file for substitutions |
| `--no-redirect` | Don't follow redirects |
| `--no-verify` | Disable SSL verification |
| `--timeout SECS` | Timeout in seconds (default: 30) |
| `--curl-only` | Print curl without sending |
| `--save` | Save to history even with `--curl-only` |
| `--gui` | Open Textual TUI |

---

## 3. GUI Mode

```bash
curlcmd --gui
```

```
┌────────────────────────┬─────────────────────────┐
│   Request              │   Response               │
│  • Method (Select)     │  • status + timing       │
│  • URL (Input)         │  • headers (table)       │
│  • Headers (TextArea)  │  • body (highlighted)    │
│  • Params (TextArea)   │                          │
│  • Body (TextArea)     ├─────────────────────────┤
│  • Auth (Select+Input) │   Generated curl         │
│  • [Send] [Curl Only]  │  • updates live          │
├────────────────────────┴─────────────────────────┤
│   History                                         │
│   ID | Timestamp | Method | URL | Status | ms     │
│   [Replay] [Show Curl] [Delete]                   │
└───────────────────────────────────────────────────┘
```

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `Ctrl+Enter` | Send request |
| `Ctrl+L` | Clear form |
| `Ctrl+H` | Focus history panel |
| `Q` | Quit |

The curl panel updates in real time as you type. Clicking **Replay** in the history panel
pre-fills the form and sends the request. **Show Curl** displays the stored curl command.

---

## 4. History

Requests are stored in `~/.curlcommander/history.db` (SQLite).

```bash
curlcmd history          # tabular view of last 30 entries
curlcmd replay <id>      # re-send a previous request
curlcmd curl <id>        # extract the curl command
curlcmd clear-history    # wipe all entries
```

The database persists across sessions and is created automatically on first run.

---

## 5. Roadmap

- [ ] Environment variables / variable substitution in URLs and headers
- [ ] Request collections — save and organise named requests
- [ ] Response diffing between history entries
- [ ] Export history to JSON / Postman collection format
- [ ] Response time graph in the GUI history panel
- [ ] Plugin system for custom auth schemes
