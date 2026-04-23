# Checkmate scripts

Offline utilities for the Checkmate plugin. The plugin itself runs
inside Cowork; these scripts run on your local machine (or a service
account on a schedule) and produce artifacts the plugin consumes.

## `build-precedent-index.py`

Walks the `Spare General` Google Drive folder, extracts every answered
row from every completed RFP response matrix, and writes a
`precedents.jsonl` corpus consumed at runtime by the
`checkmate-precedents` MCP server.

### First-run setup

1. Create a Google Cloud project and enable both the Drive API and the
   Sheets API.
2. Create an OAuth client credential of type "Desktop app" and download
   the JSON. Save it at `~/.checkmate/credentials.json`.
3. From the plugin root:

   ```bash
   cd scripts
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib openpyxl
   python build-precedent-index.py
   ```

4. A browser window opens for OAuth consent. Grant read access to
   Drive. A refresh token is cached at `~/.checkmate/token.json` for
   subsequent runs.

The default output path is `<plugin-root>/data/precedents.jsonl`, which
is what `.mcp.json` points the server at. You can override with
`--output`.

### Subsequent runs

```bash
python build-precedent-index.py
```

No further auth required (the cached refresh token handles it). Expect
the run to take several minutes depending on how many matrices are in
`Spare General`.

### Ritual

Re-run the builder:
- Weekly (automated or calendared)
- Any time a new completed RFP response lands in Drive
- After the MTD submission wraps, with the MTD response added to the
  corpus

Every re-run writes a fresh `precedents.jsonl`. The MCP server picks up
changes on the next restart (i.e., next plugin reload in Cowork).

### Schema of a precedent row

```json
{
  "id": "<drive_file_id>:<sheet_name>:<row_number>",
  "source_file": "Laramie RFP - Spare EAM Response Matrix (Updated)",
  "source_row": "Sheet1 row 5",
  "agency": "Laramie",
  "year": 2026,
  "requirement": "Enable preventive maintenance scheduling by time, mileage, or hours.",
  "verdict": "Y",
  "comment": "PM schedules can be set by calendar interval, mileage, or engine hours...",
  "url": "https://docs.google.com/spreadsheets/d/..."
}
```

### What the script does and does not do

Does: walk Drive, detect matrix schema, extract answered rows, infer
agency and year from filenames and modified timestamps.

Does NOT: compute embeddings, persist vectorized indexes, handle
incremental updates. Rebuilds the whole corpus on every run. For
corpora under ~10,000 rows this is fast enough; larger corpora would
warrant caching, which v1.0 does not implement.
