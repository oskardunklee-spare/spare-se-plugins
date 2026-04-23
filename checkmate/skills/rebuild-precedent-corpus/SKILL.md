---
name: rebuild-precedent-corpus
description: Rebuild Checkmate's precedent corpus from the Spare General Google Drive folder. Walks the folder via the Drive connector, parses every past-RFP matrix, and publishes a fresh precedents.jsonl back to Drive so fill-rfp-matrix pulls the current corpus on its next run. Trigger this skill when the user says "rebuild the precedent corpus," "refresh Checkmate's corpus," "update the precedents," "reindex Spare General," or when the Cowork schedule skill fires a weekly Checkmate rebuild. Also trigger after a new completed RFP response lands in Spare General.
---

# Rebuild Precedent Corpus

Walks `Spare General` via the Google Drive connector, parses every completed RFP matrix, and publishes a fresh `precedents.jsonl` back to Drive at `Spare General/_checkmate/precedents.jsonl`. The `fill-rfp-matrix` skill pulls from that file on its next run; the `checkmate-precedents` MCP server hot-reloads the corpus automatically.

## Prerequisites

- Google Drive connector installed and authenticated in Cowork.
- `openpyxl` available in the sandbox Python (installed once per session with `pip install openpyxl --break-system-packages`; no terminal work for the user).

## What the skill does

1. Sets up a clean working directory at `/tmp/checkmate-rebuild/` and a staging output file at `/tmp/checkmate-rebuild/precedents.jsonl`.
2. Uses the Drive connector to locate `Spare General` and walk it recursively, collecting every file whose name or mimeType looks like an RFP matrix (xlsx, csv, Google Sheet).
3. For each matrix file, downloads the bytes via the Drive connector, writes them to disk, and runs `scripts/parse_matrix.py` to append every detected answered row to the staging JSONL.
4. Validates the staging file is non-empty and JSON-line-valid.
5. Uploads the staging file to Drive at `Spare General/_checkmate/precedents.jsonl`, overwriting any previous version.
6. Copies it to `~/.cache/checkmate/precedents.jsonl` so the current session can use the fresh corpus immediately.
7. Writes a short summary (files processed, rows indexed, agencies represented) and hands control back to the user.

## Operating order

Execute the steps in this order. Do not skip steps. Do not attempt to walk Drive by any mechanism other than the connector.

### Step 1: Install openpyxl in the sandbox

Run once per session:

```bash
pip install openpyxl --break-system-packages 2>&1 | tail -1
```

If this fails in the current sandbox, stop and tell the user the rebuild cannot proceed. Do not fall back to partial extraction; a partial corpus will silently break `fill-rfp-matrix` for whatever precedents are missing.

### Step 2: Prepare the working directory

```bash
rm -rf /tmp/checkmate-rebuild
mkdir -p /tmp/checkmate-rebuild/downloads
: > /tmp/checkmate-rebuild/precedents.jsonl
```

### Step 3: Locate Spare General

Call the Drive connector's file-search tool for a folder named exactly `Spare General`. Record the folder id.

If multiple folders match, use the one owned by the Spare organization (Oskar is a member). If none match, stop and tell the user; the rebuild cannot proceed without Spare General.

### Step 4: Walk the folder recursively

Use the Drive connector to list everything under the Spare General folder id, descending into every subfolder. Collect file metadata for:

- `.xlsx` files
- `.csv` files
- Google Sheets (mimeType `application/vnd.google-apps.spreadsheet`), which the connector exports as xlsx on download

Ignore everything else (PDFs, Docs, images, the `_checkmate` subfolder if it exists).

It is fine if this takes several connector calls. Accumulate a full file list before downloading.

### Step 5: Download and parse every matrix

For each file:

1. Download its contents via the Drive connector and save to `/tmp/checkmate-rebuild/downloads/<file_id>.<ext>`. For Google Sheets, request export as xlsx.
2. Invoke the parser:

   ```bash
   python3 <plugin-root>/skills/rebuild-precedent-corpus/scripts/parse_matrix.py \
       --input /tmp/checkmate-rebuild/downloads/<file_id>.<ext> \
       --source-file "<original filename from Drive>" \
       --source-id "<drive file id>" \
       --url "<drive webViewLink if available>" \
       --output /tmp/checkmate-rebuild/precedents.jsonl
   ```

3. Exit code 0 means rows were written. Exit code 2 means the file was not a recognizable matrix, which is fine, skip it. Exit code 3 means a parse error, log the filename and move on.

Continue until every discovered file has been attempted.

### Step 6: Validate the staging file

```bash
python3 -c "
import json, sys
n = 0
with open('/tmp/checkmate-rebuild/precedents.jsonl') as f:
    for line_no, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except Exception as e:
            sys.exit(f'line {line_no}: {e}')
        n += 1
print(f'ok: {n} valid precedent rows')
"
```

If the row count is zero or well below what you saw last run, stop and tell the user something changed in Spare General. Do not overwrite the published corpus with an empty or sharply-shrunk one.

### Step 7: Publish to Drive

1. Find or create the subfolder `Spare General/_checkmate` via the Drive connector.
2. Upload `/tmp/checkmate-rebuild/precedents.jsonl` to that folder, overwriting any previous `precedents.jsonl` by file id.
3. The connector's file-create tool typically accepts a parent folder id and file content; use it.

### Step 8: Copy to local cache for the current session

```bash
mkdir -p ~/.cache/checkmate
cp /tmp/checkmate-rebuild/precedents.jsonl ~/.cache/checkmate/precedents.jsonl
```

The MCP server hot-reloads on mtime change, so any `search_precedents` call during this session sees the new corpus without a restart.

### Step 9: Summary

Report to the user:

- Number of files processed
- Number of precedent rows written
- Agencies represented (distinct count and list)
- Year range
- A Drive link to the published `precedents.jsonl`

## Scheduling

To run this weekly without manual invocation, use Cowork's built-in `schedule` skill:

> "Schedule the Checkmate precedent rebuild to run every Monday at 6am."

Cowork's scheduler will launch a session at that time, invoke this skill, and exit. The Drive connector's OAuth token persists across sessions so no reauth is needed.

## Failure modes and handling

- **Drive connector returns no Spare General**: stop; do not proceed with a partial corpus. The user's Drive connector may have lost auth, or the folder may have been moved.
- **openpyxl install fails**: stop; tell the user. Without it, xlsx parsing is impossible and the corpus will be skewed.
- **Parser exits 3 on a file**: log the filename and continue. One broken file should not block the rebuild of the whole corpus. The summary should note any such skips.
- **Published corpus is much smaller than last time**: stop and tell the user before overwriting. A sudden drop usually means a rename or permissions change in Drive, not that the content genuinely shrank.

## Never

- Do not attempt to authenticate to Google Drive directly. Always go through the Cowork connector.
- Do not run `pip install google-api-python-client` or similar. The old OAuth-based script is gone. This skill relies on the connector exclusively.
- Do not emit the intermediate `/tmp/checkmate-rebuild/downloads/*` files as outputs; they are ephemeral.
- Do not edit or delete any file in `Spare General` other than `Spare General/_checkmate/precedents.jsonl`.
