---
name: rebuild-precedent-corpus
description: Rebuild Checkmate's precedent corpus from the Spare General Google Shared Drive. Walks the Shared Drive via the Drive connector, parses every past-RFP matrix, and publishes a fresh precedents.jsonl back to Drive so fill-rfp-matrix pulls the current corpus on its next run. Trigger this skill when the user says "rebuild the precedent corpus," "refresh Checkmate's corpus," "update the precedents," "reindex Spare General," or when the Cowork schedule skill fires a weekly Checkmate rebuild. Also trigger after a new completed RFP response lands in Spare General.
---

# Rebuild Precedent Corpus

Walks `Spare General` (a Google Shared Drive) via the Drive connector, parses every completed RFP matrix, and publishes a fresh `precedents.jsonl` back to Drive at `Spare General/_checkmate/precedents.jsonl`. The `fill-rfp-matrix` skill pulls from that file on its next run; the `checkmate-precedents` MCP server hot-reloads the corpus automatically.

## Spare General is a Google Shared Drive, not a My Drive folder

**This is the most important thing to get right.** `Spare General` is a Shared Drive (formerly Team Drive). Its root ID starts with `0A`, not `1` like a regular My Drive folder. That means every Drive connector call that lists or searches content inside it MUST pass Shared Drive flags, or Google will return zero results silently.

When calling any Drive search or list tool, pass these parameters (or their connector-equivalents):

- `supportsAllDrives: true`
- `includeItemsFromAllDrives: true`
- `corpora: "drive"` with `driveId: <the Shared Drive root ID>` (or `corpora: "allDrives"` as a broader fallback)

If the connector tool's schema exposes those parameters by different names, use the equivalent. If the connector tool does not expose them at all, fall back to `get_file_metadata` + `download_file_content` on explicit file IDs (those usually work cross-drive) and walk children via `q="'<parent_id>' in parents"` queries with whatever flags the tool does accept.

### Spare General Shared Drive configuration

```
Shared Drive name: Spare General
Shared Drive root ID: 0AIjutkwbzFjJUk9PVA
Shared Drive URL:    https://drive.google.com/drive/u/0/folders/0AIjutkwbzFjJUk9PVA
```

**If the root ID ever changes** (the Shared Drive gets recreated, for example), update it in this file AND in `skills/fill-rfp-matrix/SKILL.md`. Both skills reference it.

## Prerequisites

- Google Drive connector installed and authenticated in Cowork.
- Access to the `Spare General` Shared Drive with at least Content Manager role (needed to write the published corpus).
- `openpyxl` available in the sandbox Python (installed once per session with `pip install openpyxl --break-system-packages`; no terminal work for the user).

## What the skill does

1. Sets up a clean working directory under the session scratch root (do not use `/tmp/checkmate-rebuild/` blindly; it may be owned by a prior session user).
2. Resolves the Spare General Shared Drive root, primary by hardcoded ID, fallback by name-search.
3. Walks the Shared Drive recursively with proper Shared Drive flags, collecting every file whose name or mimeType looks like an RFP matrix (xlsx, csv, Google Sheet).
4. For each matrix file, downloads the bytes via the Drive connector, writes them to disk, and runs `scripts/parse_matrix.py` to append every detected answered row to the staging JSONL.
5. Validates the staging file is non-empty and JSON-line-valid.
6. Publishes the staging file to Drive at `Spare General/_checkmate/precedents.jsonl`, overwriting any previous version.
7. Copies it to `~/.cache/checkmate/precedents.jsonl` so the current session can use the fresh corpus immediately.
8. Writes a short summary (files processed, rows indexed, agencies represented) and hands control back to the user.

## Operating order

Execute the steps in this order. Do not skip steps. Do not attempt to walk Drive by any mechanism other than the connector.

### Step 1: Install openpyxl in the sandbox

Run once per session:

```bash
pip install openpyxl --break-system-packages 2>&1 | tail -1
```

If this fails in the current sandbox, stop and tell the user the rebuild cannot proceed. Do not fall back to partial extraction; a partial corpus will silently break `fill-rfp-matrix` for whatever precedents are missing.

### Step 2: Prepare the working directory

Use a scratch directory under the current session, not `/tmp/checkmate-rebuild/` (that path can be owned by a prior sandbox user). Example:

```bash
SCRATCH="$(pwd)/checkmate-rebuild"
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/downloads"
: > "$SCRATCH/precedents.jsonl"
echo "scratch=$SCRATCH"
```

Record `$SCRATCH` and use it for every subsequent download path in this run.

### Step 3: Resolve the Spare General Shared Drive root

**Primary (by hardcoded ID):** Call `get_file_metadata` (or the connector's equivalent) on `fileId = "0AIjutkwbzFjJUk9PVA"` with `supportsAllDrives: true`. A successful response with a drive- or folder-like mimeType means that ID is usable as the walk root. Record it as `$DRIVE_ROOT_ID`.

**Backup (by name):** If the hardcoded ID lookup fails (404, permission denied, or connector rejects Shared Drive IDs), search for the Shared Drive by name. Issue a search with:

- `q: "name = 'Spare General' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"`
- `supportsAllDrives: true`
- `includeItemsFromAllDrives: true`
- `corpora: "allDrives"`

If that returns zero results, try `corpora: "drive"` iteratively across the user's Shared Drives (list the user's drives first via the connector's Shared Drive listing if it exposes one). Use the first match whose owner is the Spare organization.

**If both fail,** stop and tell the user. Do not proceed with a partial or My-Drive-only corpus. Report what was tried so the user can fix the connector auth or re-share the drive.

### Step 4: Walk the Shared Drive recursively

Use the connector's file-search tool (`search_files` or equivalent) with these parameters on every call:

- `q: "'<parent_id>' in parents and trashed = false"`
- `supportsAllDrives: true`
- `includeItemsFromAllDrives: true`
- `corpora: "drive"` with `driveId: $DRIVE_ROOT_ID`

Start with `<parent_id> = $DRIVE_ROOT_ID` and BFS through every subfolder. Collect file metadata (id, name, mimeType, webViewLink, modifiedTime, parents) for:

- `.xlsx` files (mimeType `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
- `.csv` files (mimeType `text/csv`)
- Google Sheets (mimeType `application/vnd.google-apps.spreadsheet`), which the connector exports as xlsx on download

Ignore everything else (PDFs, Docs, images, and the `_checkmate/` subfolder if it exists).

Accumulate a full file list before downloading. If the first list call returns zero children for the root, halt and report. A Shared Drive with zero children is far more likely a connector-flag bug than an empty drive.

### Step 5: Download and parse every matrix

For each file in the accumulated list:

1. Download its contents via the Drive connector (`download_file_content` or equivalent) and save to `$SCRATCH/downloads/<file_id>.<ext>`. For Google Sheets, request export as xlsx. Pass `supportsAllDrives: true` on the download call.
2. Invoke the parser:

   ```bash
   python3 <plugin-root>/skills/rebuild-precedent-corpus/scripts/parse_matrix.py \
       --input "$SCRATCH/downloads/<file_id>.<ext>" \
       --source-file "<original filename from Drive>" \
       --source-id "<drive file id>" \
       --url "<drive webViewLink if available>" \
       --output "$SCRATCH/precedents.jsonl"
   ```

3. Exit code 0 means rows were written. Exit code 2 means the file was not a recognizable matrix, which is fine, skip it. Exit code 3 means a parse error, log the filename and move on.

Continue until every discovered file has been attempted.

### Step 6: Validate the staging file

```bash
python3 -c "
import json, sys
n = 0
with open('$SCRATCH/precedents.jsonl') as f:
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

If the row count is zero, stop and report before overwriting anything in Drive. Zero almost always means the Shared Drive walk returned nothing, which is a connector-flag problem, not a real empty drive.

If the row count is >0 but sharply lower than the last run, still publish (the post-submission ritual sometimes moves files around), but call out the drop in the summary.

### Step 7: Publish to Drive

1. Find or create the `_checkmate` subfolder inside the Spare General Shared Drive root. Search:

   - `q: "name = '_checkmate' and '$DRIVE_ROOT_ID' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"`
   - `supportsAllDrives: true`, `includeItemsFromAllDrives: true`, `corpora: "drive"`, `driveId: $DRIVE_ROOT_ID`

   If it doesn't exist, create it via the connector's `create_file` tool with:
   - `name: "_checkmate"`
   - `mimeType: "application/vnd.google-apps.folder"`
   - `parents: ["$DRIVE_ROOT_ID"]`
   - `supportsAllDrives: true`

2. Find any existing `precedents.jsonl` under `_checkmate`. If present, note its fileId so you can overwrite in place.

3. Upload `$SCRATCH/precedents.jsonl`. If a previous fileId exists, use the connector's update-file operation (`files.update` wrapper) against that fileId with `supportsAllDrives: true`. Otherwise create a new file with `parents: ["<_checkmate folder id>"]` and `supportsAllDrives: true`.

4. Record the published fileId and webViewLink for the summary.

### Step 8: Copy to local cache for the current session

```bash
mkdir -p ~/.cache/checkmate
cp "$SCRATCH/precedents.jsonl" ~/.cache/checkmate/precedents.jsonl
```

The MCP server hot-reloads on mtime change, so any `search_precedents` call during this session sees the new corpus without a restart.

### Step 9: Summary

Report to the user:

- Number of files processed
- Number of precedent rows written
- Agencies represented (distinct count and list)
- Year range
- A Drive link to the published `precedents.jsonl` (webViewLink)

## Scheduling

To run this weekly without manual invocation, use Cowork's built-in `schedule` skill:

> "Schedule the Checkmate precedent rebuild to run every Monday at 6am."

Cowork's scheduler will launch a session at that time, invoke this skill, and exit. The Drive connector's OAuth token persists across sessions so no reauth is needed.

## Failure modes and handling

- **Shared Drive flags missing from connector tool schema**: look up the tool's actual parameter names and retry. If the connector truly does not support Shared Drive queries, escalate, do not proceed with a My-Drive-only walk (which will return nothing).
- **Hardcoded root ID invalid**: fall through to the name-based backup in Step 3.
- **Neither primary nor backup locates Spare General**: stop. Do not proceed with a partial corpus. The Drive connector may have lost auth, the user may not have access, or the Shared Drive root ID has changed and needs a plugin update.
- **openpyxl install fails**: stop; tell the user. Without it, xlsx parsing is impossible and the corpus will be skewed.
- **Parser exits 3 on a file**: log the filename and continue. One broken file should not block the rebuild of the whole corpus. The summary should note any such skips.
- **Published corpus is much smaller than last time**: publish but call out the drop in the summary.
- **Published corpus is zero rows**: do not publish. Stop and report.

## Never

- Do not attempt to authenticate to Google Drive directly. Always go through the Cowork connector.
- Do not run `pip install google-api-python-client` or similar. The old OAuth-based script is gone. This skill relies on the connector exclusively.
- Do not emit the intermediate `$SCRATCH/downloads/*` files as outputs; they are ephemeral.
- Do not edit or delete any file in `Spare General` other than `Spare General/_checkmate/precedents.jsonl`.
- Do not silently fall back to the bundled 10-row sample corpus. If the Shared Drive walk fails, halt loudly.
