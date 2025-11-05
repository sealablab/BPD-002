# Cursor Configuration Guide - BPD-002

**Version:** 1.0  
**Purpose:** Cursor-specific adaptation of Progressive Disclosure Architecture (PDA)  
**Audience:** Cursor users and AI assistants working in this repository

---

## Overview

This repository uses **Progressive Disclosure Architecture (PDA)** for token-efficient navigation. This document adapts the CLAUDE-centric documentation pattern specifically for Cursor while maintaining full compatibility with the existing PDA structure.

**Key Insight:** Cursor's context loading works seamlessly with PDA's three-tier system. The `.cursorrules` file provides persistent instructions, while this document explains the Cursor-specific patterns.

---

## Cursor Integration with PDA

### How Cursor Works with PDA

Cursor automatically loads `.cursorrules` at the start of each session. This file contains the navigation instructions that teach Cursor to:

1. ✅ Start with Tier 1 (`llms.txt` files)
2. ✅ Escalate to Tier 2 (`CLAUDE.md` or `CURSOR.md`) when needed
3. ✅ Load Tier 3 (source code) only when implementing
4. ✅ Trust the four authoritative sources in git submodules

### Cursor vs CLAUDE.md Pattern

| Aspect | CLAUDE.md Pattern | Cursor Adaptation |
|--------|------------------|-------------------|
| **Persistent Instructions** | Manual prompt per session | `.cursorrules` (automatic) |
| **Tier 2 Documentation** | `CLAUDE.md` files | `CLAUDE.md` OR `CURSOR.md` (both work) |
| **Navigation Prompt** | Read from `.claude/shared/` | Built into `.cursorrules` |
| **Context Loading** | Manual tier selection | Automatic via rules |
| **Authoritative Sources** | Same four submodules | Same four submodules |

**Result:** Cursor gets the same PDA benefits with automatic persistence via `.cursorrules`.

---

## Three-Tier Documentation System

### Tier 1: Quick Reference (Always Load First)

**Files:** All `llms.txt` files (~150-200 lines each)  
**Purpose:** Essential facts, API surface, common tasks  
**Token cost:** ~500-1000 tokens each

**Load these first:**
1. Root `llms.txt` - BPD-002 project structure
2. Component-specific `llms.txt` if working in specific area

**BPD Components:**
- `bpd/bpd-core/llms.txt` - Generic probe framework
- `bpd/bpd-drivers/llms.txt` - Probe-specific drivers
- `bpd/bpd-vhdl/llms.txt` - VHDL probe interface

**Upstream Libraries (Authoritative Sources):**
- `tools/forge-codegen/llms.txt` - YAML → VHDL generation
- `libs/forge-vhdl/llms.txt` - VHDL utilities
- `libs/moku-models/llms.txt` - Moku platform specs
- `libs/riscure-models/llms.txt` - DS1120A probe specs

### Tier 2: Deep Context (Load When Designing/Integrating)

**Files:** `CLAUDE.md` or `CURSOR.md` files (~3-5k tokens each)  
**Purpose:** Design rationale, integration patterns, development workflows  
**When:** Designing new features, understanding architecture

**BPD Deep Dives:**
- `bpd/bpd-core/CLAUDE.md` - Framework architecture
- `bpd/bpd-drivers/CLAUDE.md` - Driver development guide
- `bpd/bpd-vhdl/CLAUDE.md` - VHDL interface architecture

**Upstream Deep Dives:**
- `tools/forge-codegen/CLAUDE.md` - Code generation internals
- `libs/forge-vhdl/CLAUDE.md` - VHDL design patterns
- `libs/moku-models/CLAUDE.md` - Platform integration
- `libs/riscure-models/CLAUDE.md` - Probe specifications

**Note:** In Cursor, you can use either `CLAUDE.md` or `CURSOR.md` for Tier 2. Both work identically. The repository uses `CLAUDE.md` for consistency across AI assistants, but Cursor-specific documentation can use `CURSOR.md` if preferred.

### Tier 3: Implementation (Load When Modifying Code)

**Files:** Source code, tests, specialized docs  
**Purpose:** Detailed implementation logic  
**When:** Actually writing/modifying code

**Load selectively:**
- Source files in specific submodules
- Test files for validation
- `.claude/agents/*/agent.md` (monorepo orchestration agents)

---

## Decision Tree for Cursor

### Starting a New Task

```
User request arrives
    ↓
Cursor loads .cursorrules (automatic)
    ↓
Load Tier 1: llms.txt (always)
    ↓
Is this a quick question?
    ↓ Yes → Answer from Tier 1
    ↓ No
    ↓
Does this involve design/integration?
    ↓ Yes → Load Tier 2: CLAUDE.md or CURSOR.md
    ↓ No
    ↓
Does this involve implementation/debugging?
    ↓ Yes → Load Tier 3: Source code
```

### Examples by Question Type

**Quick Questions (Tier 1 only):**
- "What voltage does Moku:Go output?"
  - → Loads `libs/moku-models/llms.txt` (~500 tokens)
  - → Answers: "125 MHz, analog outputs 0-3.3V"
  - → Done! (0.25% token budget used)

**Design Questions (Tier 1 + 2):**
- "How do I add a new probe driver?"
  - → Loads `bpd/bpd-drivers/llms.txt` (~500 tokens)
  - → Needs more detail
  - → Loads `bpd/bpd-drivers/CLAUDE.md` (~3k tokens)
  - → Gets complete driver development guide
  - → Done! (1.75% token budget used)

**Implementation Questions (Tier 1 + 2 + 3):**
- "Show me the DS1120A implementation"
  - → Loads `bpd/bpd-drivers/llms.txt` (~500 tokens)
  - → Loads `bpd/bpd-drivers/CLAUDE.md` (~3k tokens)
  - → Loads `bpd/bpd-drivers/src/bpd_drivers/ds1120a.py` (~5k tokens)
  - → Ready to code! (4.25% token budget used)

---

## Four Authoritative Sources of Truth

**Always trust these libraries (in git submodules):**

1. **libs/moku-models/** - Moku platform specifications
   - Platform constants: `MOKU_GO_PLATFORM`, `MOKU_LAB_PLATFORM`, `MOKU_PRO_PLATFORM`, `MOKU_DELTA_PLATFORM`
   - Clock frequencies, voltage ranges, I/O configurations
   - **Never guess** platform specs - always read from here

2. **libs/riscure-models/** - DS1120A probe specifications
   - Platform constant: `DS1120A_PLATFORM` (450V, 64A, fixed 50ns pulse)
   - Electrical specifications, voltage ranges
   - **Never guess** probe specs - always read from here

3. **libs/forge-vhdl/** - VHDL utilities and components
   - Three voltage domains: 3.3V, 5V, ±5V
   - Reusable VHDL packages (clock dividers, LUTs, voltage packages)
   - CocoTB progressive testing infrastructure

4. **tools/forge-codegen/** - YAML → VHDL code generator
   - 23-type system with automatic register packing
   - Type-safe register serialization (50-75% register space savings)
   - Entry point: `python -m forge_codegen.generator.codegen spec.yaml`

**Never:**
- ❌ Infer types that don't exist
- ❌ Guess platform clock frequencies
- ❌ Assume voltage compatibility without validation
- ❌ Use enums for FSM states (Verilog incompatible!)

---

## Cursor-Specific Features

### Persistent Instructions via `.cursorrules`

The `.cursorrules` file is automatically loaded by Cursor at the start of each session. This provides:

- ✅ **Automatic navigation** - No need to paste prompts each session
- ✅ **Context persistence** - Rules persist across Cursor sessions
- ✅ **Token efficiency** - Same PDA benefits as CLAUDE.md pattern
- ✅ **Compatibility** - Works seamlessly with existing CLAUDE.md files

### Using Cursor Chat

When using Cursor's chat feature:

1. **Cursor automatically loads `.cursorrules`** - You don't need to do anything
2. **Start asking questions** - Cursor will navigate using PDA
3. **Cursor will escalate tiers** - Automatically loads deeper context as needed
4. **95% token budget available** - For actual work instead of context loading

### Cursor Composer

When using Cursor Composer for multi-file edits:

- Cursor will follow the same tiered loading strategy
- It will load source code (Tier 3) only for files being edited
- Design context (Tier 2) will be loaded when understanding architecture
- Quick reference (Tier 1) is always available

---

## Git Submodule Workflow

**Important:** This repository uses git submodules for authoritative sources.

```bash
# Initialize all submodules (if not already done)
git submodule update --init --recursive

# Verify submodules are present
ls libs/moku-models/llms.txt     # Should exist
ls libs/riscure-models/llms.txt  # Should exist
ls libs/forge-vhdl/llms.txt      # Should exist
ls tools/forge-codegen/llms.txt  # Should exist
```

**If submodules are missing**, Cursor will detect this (via `.cursorrules`) and offer to initialize them.

---

## Best Practices for Cursor Users

### 1. Trust the System

Cursor will automatically navigate using PDA. You don't need to manually load files - just ask questions.

### 2. Use Natural Language

Ask questions naturally:
- "What voltage does Moku:Go output?"
- "How do I add a laser FI probe driver?"
- "Show me the DS1120A implementation"

Cursor will automatically:
- Load the right tier of documentation
- Navigate to authoritative sources
- Escalate as needed

### 3. Verify Authoritative Sources

When Cursor provides specifications, verify it's reading from authoritative sources:
- ✅ "According to `libs/moku-models/llms.txt`: Moku:Go = 125 MHz"
- ❌ "I think Moku:Go runs at around 100-200 MHz..."

### 4. Let Cursor Handle Context Loading

Don't manually load files unless debugging. Cursor will:
- Start with Tier 1 automatically
- Escalate to Tier 2 when needed
- Load Tier 3 only when implementing

---

## Troubleshooting

### "Cursor isn't finding the llms.txt files"

**Possible causes:**
1. Git submodules not initialized
   - **Fix:** Run `git submodule update --init --recursive`
   - Cursor should detect this automatically via `.cursorrules`

2. `.cursorrules` not loaded
   - **Fix:** Cursor should load automatically, but verify the file exists
   - Check: `.cursorrules` should be at repository root

### "Cursor is still loading tons of source code"

**Possible causes:**
1. You asked it to implement something (expected behavior)
   - Implementation tasks require Tier 3 (source code)
   - This is correct behavior

2. Cursor didn't receive `.cursorrules`
   - **Fix:** Verify `.cursorrules` exists at repository root
   - Cursor should load it automatically

### "Submodules are empty after cloning"

**Fix:**
```bash
git submodule update --init --recursive
```

If that doesn't work:
```bash
git submodule sync
git submodule update --init --recursive
```

---

## Compatibility with CLAUDE.md Pattern

**This Cursor adaptation is fully compatible with the existing CLAUDE.md pattern:**

- ✅ Same three-tier system (llms.txt → CLAUDE.md/CURSOR.md → source)
- ✅ Same four authoritative sources (submodules)
- ✅ Same navigation decision tree
- ✅ Same token optimization strategy
- ✅ Works alongside CLAUDE.md files (no conflicts)

**Key difference:** Cursor uses `.cursorrules` for persistent instructions instead of manual prompts.

---

## Additional Resources

- **Context management:** `.claude/shared/CONTEXT_MANAGEMENT.md`
- **AI navigation (general):** `HUMAN_AI_JUMPSTART.md`
- **Architecture overview:** `.claude/shared/ARCHITECTURE_OVERVIEW.md` (v2.0)
- **Root navigation:** `llms.txt` (start here!)

---

**Version:** 1.0  
**Last Updated:** 2025-11-05  
**Maintained by:** BPD Development Team  
**Compatible with:** Cursor, Claude Code, GitHub Copilot, and other AI assistants

