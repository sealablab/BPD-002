# AI Navigation Prompt for PDA-Structured Repositories

**Context:** You are assisting a developer who has cloned a repository that follows the Progressive Context Disclosure (PDA) architecture pattern. This repository uses a three-tier documentation system designed for token-efficient navigation.

**Your task:** Help the developer navigate and work with this codebase efficiently by following the structured approach below.

---

## 🔄 Fresh Context Window Protocol

**If this is a new conversation or fresh context window:**

This prompt should persist across context resets. When starting fresh:

1. **Re-run Phase 1** (Repository Integrity Check)
   - Verify submodules still initialized
   - Don't assume previous session state

2. **Re-read `/llms.txt`** to re-orient
   - Takes ~500 tokens, ensures correct navigation
   - Better to re-read than guess from stale memory

3. **Ask user for context** if needed
   - "What were you working on before?"
   - "Which component should I focus on?"

4. **Don't hallucinate previous session state**
   - If you don't remember something, re-read the docs
   - Better to load 500 tokens than guess incorrectly

**Testing fresh context:** The user may test you by asking "Can you verify the repository is set up correctly?" after a context reset. You should:
- Run the pre-flight checklist (Phase 1)
- List all 4 authoritative llms.txt files (in libs/ and tools/ submodules)
- Confirm you understand the three-tier pattern

---

## Phase 1: Repository Integrity Check (Pre-Flight)

**Objective:** Verify the repository is correctly initialized before navigation.

### Step 1: Check for Git Submodules

This repository uses git submodules for library dependencies (`libs/`) and development tools (`tools/`).

**Action required:** Check if the following directories exist:
- `libs/`
- `libs/moku-models/`
- `libs/riscure-models/`
- `libs/forge-vhdl/`
- `tools/`
- `tools/forge-codegen/`

**If any directory is missing:**

1. Alert the user with this message:
   ```
   ⚠️  Git submodules are not initialized. I can initialize them for you now.

   The following directories are missing:
     - [list missing directories]

   I'll run: git submodule update --init --recursive
   ```

2. Ask if they want you to run the command
3. If yes, execute: `git submodule update --init --recursive`
4. Verify directories now exist

**Why this matters:** Without submodules, the developer cannot access authoritative component documentation (platform specs, probe specs, VHDL utilities, code generators).

---

## Phase 2: Orient with Root Documentation

**Objective:** Understand the repository structure and identify relevant components.

### Step 1: Read Root Navigation File

Load and read: `/llms.txt`

**Expected structure:**
- Component catalog (what exists in this repo)
- High-level organization (bpd/, libs/, tools/)
- Quick reference information
- Pointers to deeper documentation

**What to extract:**
- [ ] What are the main component categories?
- [ ] What is the purpose of this repository?
- [ ] Which components exist in `bpd/`?
- [ ] Which submodules exist in `libs/` and `tools/`?

### Step 2: Identify the Navigation Pattern

Confirm the three-tier documentation structure:

**Tier 1: llms.txt** (~500 tokens)
- Quick reference
- Component catalog
- Basic usage examples
- Pointers to Tier 2

**Tier 2: CLAUDE.md** (~2-5k tokens)
- Design rationale
- Architecture details
- Integration patterns
- Development workflows

**Tier 3: Source Code** (variable tokens)
- Implementation details
- Only load when implementing or debugging

---

## Phase 3: Navigate to Relevant Component

**Objective:** Load only the documentation needed to answer the user's question.

### Decision Tree: What Component Do They Need?

**If the user asks about:**

→ **Moku platform specifications** (clock speeds, voltage ranges, I/O specs)
  - Navigate to: `libs/moku-models/llms.txt`
  - Escalate to: `libs/moku-models/CLAUDE.md` (if needed)
  - Source: `libs/moku-models/moku_models/` (only for implementation)

→ **Probe hardware specifications** (DS1120A, voltage glitching, laser FI)
  - Navigate to: `libs/riscure-models/llms.txt`
  - Escalate to: `libs/riscure-models/CLAUDE.md` (if needed)
  - Source: `libs/riscure-models/riscure_models/` (only for implementation)

→ **How to add/modify probe drivers**
  - Navigate to: `bpd/bpd-drivers/llms.txt`
  - Escalate to: `bpd/bpd-drivers/CLAUDE.md` (driver development guide)
  - Source: `bpd/bpd-drivers/src/bpd_drivers/` (for implementation)

→ **VHDL interface for fault injection**
  - Navigate to: `bpd/bpd-vhdl/llms.txt`
  - Escalate to: `bpd/bpd-vhdl/CLAUDE.md` (VHDL architecture)
  - Source: `bpd/bpd-vhdl/src/` (for VHDL implementation)

→ **Generic probe framework** (interfaces, validation, driver registry)
  - Navigate to: `bpd/bpd-core/llms.txt`
  - Escalate to: `bpd/bpd-core/CLAUDE.md` (framework design)
  - Source: `bpd/bpd-core/src/bpd_core/` (for implementation)

→ **VHDL utilities** (reusable components, voltage packages)
  - Navigate to: `libs/forge-vhdl/llms.txt`
  - Source: `libs/forge-vhdl/vhdl/` (for VHDL implementation)

→ **YAML → VHDL code generation**
  - Navigate to: `tools/forge-codegen/llms.txt`
  - Escalate to: `tools/forge-codegen/CLAUDE.md` (generator architecture)
  - Source: `tools/forge-codegen/forge_codegen/` (for implementation)

### Step 1: Load Tier 1 (Quick Reference)

Start by loading the component's `llms.txt` file.

**Token budget:** ~500 tokens per file
**Expected content:**
- Component purpose
- Core exports/capabilities
- Basic usage example
- Pointers to Tier 2 documentation

**Check:** Does this answer the user's question?
- ✅ **Yes** → Provide answer, stop here
- ❌ **No** → Proceed to Step 2 (Tier 2)

### Step 2: Escalate to Tier 2 (Design Context) - If Needed

Only load CLAUDE.md if:
- User needs design rationale or architecture context
- User is implementing something new
- Tier 1 didn't provide enough detail

**Token budget:** ~2-5k tokens per file
**Expected content:**
- Complete specifications
- Design decisions and rationale
- Integration patterns with other components
- Development workflows
- Pointers to specific source files

**Check:** Does this answer the user's question?
- ✅ **Yes** → Provide answer, stop here
- ❌ **No** → Proceed to Step 3 (Source)

### Step 3: Load Source Code - Only for Implementation

Only load source code if:
- User is implementing a feature
- User is debugging existing code
- User needs to see implementation details

**Token budget:** Variable (5-10k tokens per file)

**Important:**
- Load specific files, not entire directories
- Use pointers from CLAUDE.md to find relevant files
- Don't speculatively load source "just in case"

---

## Phase 4: Apply Core Principles

### Principle 1: Never Guess, Always Trust

**DON'T:**
- ❌ "I think Moku:Go runs at 100MHz..." (guessing)
- ❌ "The probe probably accepts 5V..." (inferring)
- ❌ "DS1120A likely has configurable pulse width..." (assuming)

**DO:**
- ✅ Read `libs/moku-models/llms.txt` → "Moku:Go = 125 MHz (authoritative)"
- ✅ Read `libs/riscure-models/llms.txt` → "DS1120A digital_glitch = 0-3.3V TTL only"
- ✅ Read `libs/riscure-models/llms.txt` → "DS1120A pulse width = 50ns (FIXED, not configurable)"

**Rule:** Always read the authoritative component's documentation. Never infer specs from similar hardware.

### Principle 2: Token Efficiency

Track your token usage:

**Quick lookup:**
- Load 1-3× llms.txt files (~500-1500 tokens)
- Budget used: <1%

**Design work:**
- Load llms.txt + CLAUDE.md (~3-6k tokens)
- Budget used: ~2-3%

**Implementation:**
- Load llms.txt + CLAUDE.md + specific source files (~8-15k tokens)
- Budget used: ~5-7%

**Goal:** Keep token usage minimal by loading only what's needed.

### Principle 3: Contextual Disclosure

**Load minimally, expand progressively:**
1. Start with root llms.txt (orientation)
2. Navigate to component llms.txt (quick reference)
3. Escalate to CLAUDE.md only if needed (design)
4. Load source only when implementing (implementation)

**Don't:**
- ❌ Load entire directories "just in case"
- ❌ Read all documentation up front
- ❌ Speculatively load source files

---

## Phase 5: Post-Navigation Validation

**Objective:** Confirm you've correctly navigated the PDA structure.

### Expected Repository Structure

```
<repo-root>/
├── llms.txt                                    # Tier 1: Root navigation
├── CLAUDE.md                                   # Tier 2: Repository overview
│
├── bpd/                                        # Application code
│   ├── bpd-core/
│   │   ├── llms.txt                            # Tier 1: Framework quick ref
│   │   ├── CLAUDE.md                           # Tier 2: Framework design
│   │   └── src/bpd_core/                       # Tier 3: Implementation
│   │
│   ├── bpd-drivers/
│   │   ├── llms.txt                            # Tier 1: Drivers quick ref
│   │   ├── CLAUDE.md                           # Tier 2: Driver patterns
│   │   └── src/bpd_drivers/                    # Tier 3: Implementation
│   │
│   └── bpd-vhdl/
│       ├── llms.txt                            # Tier 1: VHDL quick ref
│       ├── CLAUDE.md                           # Tier 2: VHDL architecture
│       └── src/                                # Tier 3: VHDL source
│
├── libs/                                       # Interface specifications (submodules)
│   ├── moku-models/
│   │   ├── llms.txt                            # Tier 1: Platform specs
│   │   ├── CLAUDE.md                           # Tier 2: Integration patterns
│   │   └── moku_models/                        # Tier 3: Pydantic models
│   │
│   ├── riscure-models/
│   │   ├── llms.txt                            # Tier 1: Probe specs
│   │   ├── CLAUDE.md                           # Tier 2: Safety patterns
│   │   └── riscure_models/                     # Tier 3: Pydantic models
│   │
│   └── forge-vhdl/
│       ├── llms.txt                            # Tier 1: VHDL components
│       └── vhdl/                               # Tier 3: VHDL packages
│
└── tools/                                      # Development tools (submodules)
    └── forge-codegen/
        ├── llms.txt                            # Tier 1: Codegen quick ref
        ├── CLAUDE.md                           # Tier 2: Generator architecture
        └── forge_codegen/                      # Tier 3: Implementation
```

### Validation Checklist

**Verify you can locate the 4 authoritative `llms.txt` files (git submodules):**

- [ ] `libs/moku-models/llms.txt` (Moku platform specs - authoritative)
- [ ] `libs/riscure-models/llms.txt` (DS1120A probe specs - authoritative)
- [ ] `libs/forge-vhdl/llms.txt` (VHDL utilities - authoritative)
- [ ] `tools/forge-codegen/llms.txt` (YAML → VHDL generator - authoritative)

**All 4 submodule files found?** ✅ You've correctly located the stable authoritative sources.

**Pattern confirmed:**
- Each component has Tier 1 (llms.txt)
- Each component has Tier 2 (CLAUDE.md) or goes straight to Tier 3
- Same pattern applies to libs/, tools/, and application code (bpd/)

---

## Additional Context

### Understanding PDA Architecture

If the user wants to understand the **why** behind this pattern:
- Read: `WIP/ARCHITECTURE_OVERVIEW_v2.0_DRAFT.md` (pedagogical explanation)
- Or refer to: `.claude/shared/CONTEXT_MANAGEMENT.md` (token optimization strategy)

### Example Workflows

**Quick specification query:**
```
User: "What voltage does Moku:Go output?"
→ Load libs/moku-models/llms.txt (~500 tokens)
→ Answer: "Moku:Go = 125 MHz, analog outputs 0-3.3V"
→ Token usage: 500 tokens (0.25% budget)
```

**Design understanding:**
```
User: "How do I add a new probe driver?"
→ Load bpd/bpd-drivers/llms.txt (~500 tokens)
→ Need more detail
→ Load bpd/bpd-drivers/CLAUDE.md (~3k tokens)
→ Get complete driver development guide
→ Token usage: 3.5k tokens (1.75% budget)
```

**Implementation:**
```
User: "Show me the DS1120A driver implementation"
→ Load bpd/bpd-drivers/llms.txt (~500 tokens)
→ Load bpd/bpd-drivers/CLAUDE.md (~3k tokens)
→ Load bpd/bpd-drivers/src/bpd_drivers/ds1120a.py (~5k tokens)
→ Ready to implement changes
→ Token usage: 8.5k tokens (4.25% budget)
```

---

## Summary of Your Approach

1. **Pre-flight:** Check submodules, offer to initialize if missing
2. **Orient:** Read root llms.txt to understand structure
3. **Navigate:** Use decision tree to find relevant component
4. **Load progressively:** Tier 1 → Tier 2 → Tier 3 (only as needed)
5. **Never guess:** Always read authoritative documentation
6. **Stay efficient:** Track token usage, minimize loading
7. **Validate:** Confirm you found the 4 authoritative llms.txt files (submodules)

**Start here:** Read `/llms.txt` and begin helping the developer navigate this codebase efficiently.

**Remember:** Focus on stable authoritative sources (libs/ and tools/ submodules) for reliable specs. Application code (bpd/) may be under development.
