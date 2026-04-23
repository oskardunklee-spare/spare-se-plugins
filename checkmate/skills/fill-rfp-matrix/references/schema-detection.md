# Schema Detection

How to programmatically identify the structure of an incoming compliance matrix. Do this before filling any row.

## Detection steps

1. **List all sheets.** Match names like `Instructions`, `Summary`, `Dropdown`, `Response Options (hidden)`, numbered sheets (`1`, `2`, `2A`, `2B`). Identify which sheets contain requirements vs. which are metadata/configuration.
2. **Find the header row on each requirement sheet.** Look for a row containing column labels that include one of: `REQ #`, `Requirement`, `System Requirement`, `Question`, `#`, `ID`.
3. **Identify the requirement column** (contains the question text).
4. **Identify the verdict column** by looking for labels like: `System Meets Requirement`, `Response`, `Bidder Response`, `Y/N/P`, `Yes/No/Mod`, `Compliance`. If unclear, the column immediately after the requirement that has data validation dropdowns is usually the verdict.
5. **Identify the comment column**, usually labeled `Comment`, `Comments`, `Response`, `Details`, `Bidder Details to Support Response`, `Spare Comments`, `Spare Response`.
6. **Find the verdict vocabulary.** Check in order:
   - Hidden sheets with names like `Response Options`, `Dropdown`, `Instructions`, list the allowed values in column A
   - Rows between the sheet title and the requirement data (e.g., MTD sheet 2A: rows 5-8 define `Y / Y-ND / N / I`; rows 11-12 define the `F / E` qualifier)
   - Data validation attached to the verdict column (openpyxl: `ws.data_validations`)
   - Any cell in the header region that says something like "Available Responses for Column F"
7. **Identify section-header rows.** Scan the requirement column for rows that have text but no sibling data in the verdict/comment columns. These are often short (e.g., `3.1 Fleet Operations`, `Customer account`) and sometimes have styling differences (bold, fill). Leave them untouched.
8. **Find the actual data range.** The first requirement row is usually the row after the header row. The last is the last row with non-null content in the requirement column.

## Observed agency layouts (reference corpus)

### HOLON Requirements Matrix

- Single sheet, two tabs (`Sheet1` blank, `WORKING ANSWER` filled)
- Columns: `A = Requirement`, `B = (unused)`, `C = Yes/No/Mod`, `D = Spare Comments`
- Header row: `R1`
- Data rows: `R2` onward
- Section-header rows are inline in column A (e.g., R2: `3.1 Fleet Operations`, R3: `System Deployment`) and have no verdict/comment

### MTD Custom Transit Solution Questionnaire (multi-sheet)

- Sheets: `Instructions`, `Summary`, `1` through `16`, `Response Options (hidden)`
- Per content sheet: title at `C2`, response definitions at rows 5-8, header at row 10, data from row 11
- Columns per content sheet: `B = internal ID`, `C = #`, `D = Question`, `F = Response`, `G = Comment`, `H = Status`

### MTD RFP #2025-008 (EAM, multi-attachment)

- Sheets: `1` through `13`, including `2A` (Assets) and `2B` (EAM)
- Content sheets 2A and 2B: header at row 18 (2A) or 19 (2B), data starts row 19 / 20
- Columns: `A = REQ #`, `B = FUNCTION`, `C = PROCESS`, `D = INTERFACE`, `E = SYSTEM REQUIREMENT`, `F = SYSTEM MEETS REQUIREMENT`, `G = SUPPORT RESPONSE`, `H = MODULE/SYSTEM`, `I = PHASE FOR GO-LIVE`, `J = IF Y-ND`, `K = COMMENTS`
- Verdict vocab rows 5-8: `Y / Y-ND / N / I`. Y-ND qualifier rows 11-12: `F (Future Release) / E (Enhancement)`. Support rows 15-17: `S / TPS / NS`
- Column K had pre-existing stray agency data (numeric scores) that must be cleared on pre-flight

### GRT (MobilityPLUS) Detailed Requirements Response

- Multi-sheet by requirement area: `Mandatory Requirements`, `Cust. Acct, Interface & Comms`, `Eligibility Management`, `Para Trip Requests & Booking`, etc.
- Columns: `A = ID`, `B = Requirement Area`, `C = Requirement Sub Area`, `D = Requirement`, `E = Region Notes`, `F = Bidder Response`, `G = Bidder Details to Support Response`, some sheets add `H = Suggested/edited Response`
- Verdict vocab from `Dropdown` sheet column A: `Fully Meet – Configuration only / Fully Meet – Customization required / Partially Meet – Configuration only / Partially Meet – Customization required / Unable - Unable to meet any of the requirement`
- Section structure is encoded in separate Requirement Area / Sub Area columns rather than inline header rows

### BC Transit RFP 24.165 Custom Transit Solution Questionnaire

- Sheets: `Instructions`, `Summary`, `1` through `16`, `Response Options (hidden)`
- Verdict vocab from hidden Response Options sheet: `Yes / No / Other`
- Response column: `F`, Comment column: `G`, Status column: `H`

### Laramie Fleet Management Software RFP

- Single sheet with inline sections (3.1 Fleet & Asset Management, 3.2 Inventory, etc.)
- Columns: `Section, #, Requirement, Y/N/P, Spare Response`
- Verdict vocab inline in the header: `Y / N / P` (Partial)

### PDRTA Specs

- Single sheet, prose-only
- Columns: `A = Requirement text`, `B = Spare Response` (prose only, no verdict column)
- Also includes internal reviewer columns (e.g., `C = Oskar review`) that are not part of the submission

## Implementation notes

- Use `openpyxl.load_workbook(path, data_only=True)` for reading (forces calculated values, avoids formula strings)
- Use `openpyxl.load_workbook(path)` for editing (preserves formulas and styles)
- Always respect the existing column order and width
- When adding internal Confidence and Reasoning columns, place them at the first column beyond the last agency-defined one (for MTD that's column L; for HOLON that's column E)
- Preserve the agency's data validation dropdowns on the verdict column by not overwriting their dropdown definitions
