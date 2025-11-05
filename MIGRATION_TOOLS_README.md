# BPD-002 → BPD-002 Migration Tools

Two Python scripts to help migrate from BPD-002 to BPD-002.

## Tools

### 1. `find_old_references.py` - Find old references

**Purpose:** Exhaustive, case-insensitive search for all BPD-002 references

**Usage:**

```bash
# Find all references (print to console)
python find_old_references.py

# Save results to file
python find_old_references.py -o report.txt

# Search specific directory
python find_old_references.py /path/to/directory
```

**What it finds:**
- `BPD-002`, `bpd-002`, `BPD_002`, `bpd_002`, `BPD002`, `bpd002`
- File content matches (with line numbers)
- File path matches (files/dirs that need renaming)

**Example output:**
```
📄 README.md (4 occurrences)
   Line   45: # BPD-002 - Basic Probe Driver
   Line   58: git clone https://github.com/sealablab/BPD-002.git
   ...

SUMMARY
Total matches:      88
Files affected:     16
```

### 2. `replace_old_references.py` - Replace references

**Purpose:** Automated replacement of BPD-002 → BPD-002 (case-preserving)

**Usage:**

```bash
# DRY RUN (preview changes, no files modified)
python replace_old_references.py

# EXECUTE replacements (with backup)
python replace_old_references.py --execute

# EXECUTE without backup
python replace_old_references.py --execute --no-backup

# Restore from backups
python replace_old_references.py --restore

# Clean up backup files
python replace_old_references.py --clean-backups
```

**What it does:**
- Replaces all variations (case-preserving):
  - `BPD-002` → `BPD-002`
  - `bpd-002` → `bpd-002`
  - `BPD_002` → `BPD_002`
  - `bpd_002` → `bpd_002`
  - etc.
- Creates `.bak` backups (unless `--no-backup`)
- Skips binary files and unwanted directories (`.git`, `__pycache__`, etc.)

## Recommended Workflow

### Step 1: Find all references
```bash
python find_old_references.py -o old_references_report.txt
```

Review `old_references_report.txt` to see what will be changed.

### Step 2: Preview replacements (dry run)
```bash
python replace_old_references.py
```

This shows what would be changed without modifying files.

### Step 3: Execute replacements
```bash
python replace_old_references.py --execute
```

This creates backups (`.bak` files) and performs replacements.

### Step 4: Test your changes
```bash
# Run tests, verify functionality
pytest
# Check git diff
git diff
```

### Step 5: Clean up or restore

**If everything works:**
```bash
python replace_old_references.py --clean-backups
```

**If something broke:**
```bash
python replace_old_references.py --restore
```

## Current Findings

**As of 2025-11-05:**

- **88 references** found across **16 files**
- No file path matches (no files/directories need renaming)
- Main files affected:
  - Documentation: `README.md`, `CLAUDE.md`, `llms.txt`, `BPD-README.md`
  - Component docs: `bpd/*/CLAUDE.md`, `bpd/*/llms.txt`
  - Claude configs: `.claude/shared/*.md`
  - Archive: `.archive/README.old.md`

## Safety Features

### `find_old_references.py`
- Read-only (never modifies files)
- Skips binary files
- Ignores `.git`, `__pycache__`, etc.
- Case-insensitive search

### `replace_old_references.py`
- **Dry run by default** (must explicitly `--execute`)
- Creates `.bak` backups (unless `--no-backup`)
- Case-preserving replacements
- Skips directories: `.git`, `__pycache__`, `node_modules`, etc.
- Can restore from backups

## What These Scripts DON'T Handle

1. **File/directory renames** - No files need renaming (script checked)
2. **Git remote URL** - Update manually:
   ```bash
   git remote set-url origin https://github.com/sealablab/BPD-002.git
   ```
3. **Git submodules** - Update `.gitmodules` manually if needed
4. **Binary files** - Not searched or modified

## Example Session

```bash
# 1. Find references
$ python find_old_references.py -o report.txt
Scanning /private/tmp/aiiii/BPD-002...
Found 88 references to old repo name
✅ Results saved to: report.txt

# 2. Preview changes
$ python replace_old_references.py
⚠️  Running in DRY RUN mode - no files will be modified
...
Files modified:       16
Total replacements:   88

# 3. Execute
$ python replace_old_references.py --execute
✓ LIVE MODE - files will be modified (backup: enabled)
  ✓ Modified: README.md
  ✓ Modified: CLAUDE.md
  ...
✓ Replacements complete!
  Backups saved with .bak extension

# 4. Test
$ git diff
$ pytest

# 5. Clean up
$ python replace_old_references.py --clean-backups
✓ Cleaned 16 backup files
```

## Notes

- Both scripts ignore the two replacement scripts themselves (no infinite loops)
- Scripts are UTF-8 aware and handle encoding errors gracefully
- Progress is printed to console in real-time
- Exit codes indicate success/failure for scripting

---

**Generated:** 2025-11-05
**Version:** 1.0
