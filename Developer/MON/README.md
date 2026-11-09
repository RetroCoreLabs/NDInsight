# SINTRAN III Monitor Calls Documentation

This directory contains the complete documentation for all 230 SINTRAN III Monitor Calls in structured YAML format, along with tools to generate comprehensive markdown documentation.

## Quick Start

**To browse monitor calls:**
- Read `ND MON Calls.md` for comprehensive documentation with indexes and examples

**To CALL a monitor call from a language:**
- PLANC: [../Languages/Application/PLANC-MONITOR-CALLS.md](../Languages/Application/PLANC-MONITOR-CALLS.md)
  - the named `MONn` routines, why `MONITOR_CALL` fails on D100, error handling, and the
  library load order.

**To update documentation:**
1. Edit YAML files in `calls/` directory
2. Run `python3 generate_mon_calls_markdown.py`
3. Review updated `ND MON Calls.md`

**To validate YAML:**
- Use `mon-call.schema.json` with JSON Schema validators
- See [Validation](#validation) section below

## Pages in this folder

| Page | What it is |
|------|------------|
| [ND MON Calls.md](ND%20MON%20Calls.md) | The generated reference for every call, with three indexes |
| [Monitor Calls.md](Monitor%20Calls.md) | The OCR text of the manual (ND-860228.2 EN) |
| [calls/60B_N500M_Functions.md](calls/60B_N500M_Functions.md) | Monitor call 60B (N500M): its functions |
| [calls/60B_N500M_Hardware_Mapping.md](calls/60B_N500M_Hardware_Mapping.md) | Monitor call 60B (N500M): how it maps to the hardware |
| [calls/SCHEMA-EMULATION-BLOCK.md](calls/SCHEMA-EMULATION-BLOCK.md) | The `emulation:` block in the YAML files: what we learned by emulating the calls, and the rules for writing it |
| [mon-call.schema.json](mon-call.schema.json) | JSON Schema for the YAML files |

## Directory Structure

```
Developer/MON/
├── calls/                           # 230 YAML files (one per monitor call)
├── mon-call.schema.json             # JSON Schema for YAML validation
├── mon-call-schema.yaml             # YAML Schema for reference
├── Monitor Calls.md                 # Original OCR source material (931K)
├── ND MON Calls.md                  # Generated comprehensive documentation (582K)
├── generate_mon_calls_markdown.py   # Script to regenerate markdown docs
└── README.md                        # This file
```

## File Descriptions

### Source Data

**`calls/`** (230 YAML files, ~600K total)
- **Purpose:** Authoritative source of truth for all monitor call documentation
- **Content:** One YAML file per monitor call (0B through 514B octal)
- **Format:** Structured data including parameters, examples in 6 languages, compatibility info
- **Usage:** Edit these files to update documentation; run generator script to rebuild markdown

**`Monitor Calls.md`** (931K)
- **Purpose:** Original OCR-scanned reference material from official Norsk Data manual
- **Content:** Complete SINTRAN III Monitor Calls manual (ND-860228.2 EN)
- **Source:** Scanned by Jonny Oddene for Sintran Data © 2020
- **Usage:** Reference material; used during initial extraction; kept for historical accuracy

### Generated Documentation

**`ND MON Calls.md`** (582K)
- **Purpose:** Human-readable comprehensive reference for all 230 monitor calls
- **Content:**
  - Three indexes (by octal number, call name, and short name)
  - Full documentation for each call with cross-references
  - Code examples in 6 languages (Pascal, COBOL, Fortran, PLANC, ASSEMBLY-500, MAC)
  - Compatibility badges and parameter descriptions
- **Generation:** Auto-generated from `calls/*.yaml` via `generate_mon_calls_markdown.py`
- **Usage:** Primary reference for developers; DO NOT edit manually; regenerate from YAML

### Schemas

**`mon-call.schema.json`** (6.9K)
- **Purpose:** JSON Schema definition for validating YAML files
- **Content:** Complete schema with all required/optional fields, types, and constraints
- **Usage:** Used by validation tools and IDEs for YAML validation

**`mon-call-schema.yaml`** (6.5K)
- **Purpose:** YAML version of schema for human readability
- **Content:** Same schema as JSON version, more readable format
- **Usage:** Reference when creating or updating YAML files

### Tools

**`generate_mon_calls_markdown.py`** (303 lines)
- **Purpose:** Generates `ND MON Calls.md` from YAML source files
- **Usage:** Run after updating any YAML files in `calls/` directory
- **Command:** `python3 generate_mon_calls_markdown.py`
- **Output:** Overwrites `ND MON Calls.md` with fresh generated content

## Regenerating Documentation

If you update any YAML files in `calls/`, regenerate the markdown documentation by running:

```bash
cd Developer/MON
python3 generate_mon_calls_markdown.py
```

This will regenerate `ND MON Calls.md` with:
- Three indexes (by octal number, call name, and short name)
- Full documentation for all 230 monitor calls
- Cross-referenced links throughout
- Code examples in 6 programming languages
- Compatibility badges

**Note:** Run this script from the repository root or the `Developer/MON` directory.

## YAML File Format

Each monitor call is documented in a YAML file with this structure:

```yaml
octal: 131B
name: DataTransfer
short_names:
  - ABSTR
description: |
  Full description with bullet points...
see_also:
  - TransferData
  - ReadFromFile
parameters:
  - name: Param1
    type: UNKNOWN
    io: I
    description: Parameter description
examples:
  pascal:
    available: true
    code: |
      DataTransfer(DeviceNo, Func, ...);
  cobol:
    available: true
    code: |
      MONITOR-CALL "DataTransfer" USING ...
  # ... other languages
compatibility:
  nd100: true
  nd500: true
  user_programs: true
  rt_programs: true
  system_programs: false
source:
  document: SINTRAN III Monitor Calls (ND-860228.2 EN)
  page: 127
extraction:
  date: '2025-01-06'
  ocr_corrected: false
```

## Validation

Validate YAML files against the schema:

```bash
# Install validation tool if needed
pip install jsonschema pyyaml

# Validate a single file
python3 -c "
import yaml, jsonschema
schema = yaml.safe_load(open('mon-call.schema.json'))
data = yaml.safe_load(open('calls/131B_DataTransfer.yaml'))
jsonschema.validate(data, schema)
print('✓ Valid')
"
```

## Statistics

**Monitor Calls Coverage:**
- **Total Monitor Calls:** 230
- **Monitor Call Range:** 0B - 514B (octal)
- **Calls with Short Names:** 230 (100%)
- **Calls with Full Documentation:** 230 (100%)

**Code Examples:**
- **Programming Languages:** 6 (Pascal, COBOL, Fortran, PLANC, ASSEMBLY-500, MAC)
- **Languages per Call:** Varies (most have all 6)

**Directory Size:**
- **Total:** ~2.2MB
- **YAML Source Files (calls/):** ~600K (230 files)
- **Generated Documentation:** 582K (ND MON Calls.md)
- **Original OCR Scan:** 931K (Monitor Calls.md)
- **Schemas & Tools:** ~23K

**Source Material:**
- **Document:** SINTRAN III Monitor Calls (ND-860228.2 EN)
- **Scanned by:** Jonny Oddene for Sintran Data © 2020
- **Extraction Date:** 2025-01-06
- **Last Cleanup:** 2025-11-06

## Workflow

### Typical Development Workflow

1. **Find a monitor call** to update:
   - Browse `ND MON Calls.md` indexes
   - Or check `calls/` directory directly

2. **Edit the YAML file**:
   ```bash
   cd Developer/MON
   # Edit the specific call, e.g.:
   nano calls/131B_DataTransfer.yaml
   ```

3. **Validate changes** (optional but recommended):
   ```bash
   python3 -c "
   import yaml, jsonschema
   schema = yaml.safe_load(open('mon-call.schema.json'))
   data = yaml.safe_load(open('calls/131B_DataTransfer.yaml'))
   jsonschema.validate(data, schema)
   print('✓ Valid')
   "
   ```

4. **Regenerate documentation**:
   ```bash
   python3 generate_mon_calls_markdown.py
   ```

5. **Review changes**:
   ```bash
   # Check the updated markdown
   less "ND MON Calls.md"
   # Or search for your specific call
   grep -A 20 "131B" "ND MON Calls.md"
   ```

6. **Commit changes**:
   ```bash
   git add calls/131B_DataTransfer.yaml "ND MON Calls.md"
   git commit -m "Update DataTransfer (131B) documentation"
   ```

## History

### Development Timeline

1. **Initial Extraction (Jan 2025)** - 195/230 calls extracted with OCR reconstruction
2. **Description Enhancement** - Full descriptions extracted from source sections
3. **Schema Cleanup** - Removed unused fields, simplified structure
4. **Short Names Population** - Added assembly mnemonics to all 230 calls
5. **Quote Fixing** - Fixed apostrophe escaping in code examples
6. **Markdown Generation** - Created comprehensive documentation with cross-references
7. **Directory Cleanup (Nov 2025)** - Removed backup files, historical extraction scripts, and redundant documentation

### Files Removed During Cleanup (Nov 6, 2025)

**Removed 189 files (~2.5MB) including:**
- `calls_backup/` - 180 old backup YAML files
- `Monitor Calls - CORRECTED.md` - Duplicate OCR scan (935K)
- `extract_mon_calls.py` - Historical extraction script
- `cleanup_yaml.py` - Historical cleanup script
- `EXTRACTION_PLAN.md` - Historical planning documentation
- `FINAL-EXTRACTION-REPORT.md` - Historical extraction report
- `SCHEMA-CLEANUP-ANALYSIS.md` - Historical schema analysis
- `extraction-report.md` - Historical mini-report
- `Mon-list.md` - Redundant simple list
- Root-level YAML samples (moved to `calls/`)

**Rationale:** Keep only essential files; git history preserves all deleted content if needed.
