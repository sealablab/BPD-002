# Context Management Strategy - BPD-002

**Version:** 1.0 (BPD-002-specific)
**Purpose:** Token optimization and tiered loading for AI agents working on BPD-002
**Audience:** AI agents working in this project

---

## Overview

BPD-002 uses a **three-tier context loading strategy** to optimize token usage while ensuring AI agents have necessary information at the right time.

**Token Budget:** 200k tokens total
- System + tools: ~16k tokens (8%)
- Target for messages: ~100k tokens (50%)
- Reserved buffer: ~84k tokens (42%)

**Problem:** Loading all documentation upfront wastes tokens on information not needed for current task.

**Solution:** Tiered loading - start minimal, drill down as needed.

---

## Three-Tier Loading Strategy

### Tier 1: Always Load First (~500-1000 tokens)

**Purpose:** Quick orientation, navigation to deeper context

**Load these first:**
1. **Root `llms.txt`** - BPD-002 project structure
2. **Root `CLAUDE.md`** - Project overview (this is loaded by default)
3. **Component-specific `llms.txt`** if working in specific area

**What you get:**
- High-level architecture
- Where to find detailed info (pointers to Tier 2)
- Common questions answered immediately
- Decision tree for what to load next

**Example - Starting work:**
```
AI Agent loads:
1. llms.txt → "BPD-002 has bpd-core, bpd-drivers, bpd-vhdl + upstream libs"
2. Root CLAUDE.md → "Multi-vendor probe integration framework for Moku"

AI Agent knows:
- Project structure
- Available components (bpd/, libs/, tools/)
- Integration patterns
- How to navigate deeper
```

---

### Tier 2: Load When Designing/Integrating (~2000-5000 tokens)

**Purpose:** Deep context for specific domains, cross-library integration

**Load these when:**
- Designing new probe drivers
- Understanding VHDL components
- Debugging integration issues
- Working with platform specifications

**Tier 2 Documents:**

1. **Component CLAUDE.md files**
   - `bpd/bpd-core/CLAUDE.md` - Framework architecture
   - `bpd/bpd-drivers/CLAUDE.md` - Driver development guide
   - `bpd/bpd-vhdl/CLAUDE.md` - VHDL interface architecture
   - `libs/moku-models/CLAUDE.md` - Platform integration
   - `libs/riscure-models/CLAUDE.md` - DS1120A specifications
   - `tools/forge-codegen/CLAUDE.md` - YAML → VHDL generation

2. **Shared knowledge docs**
   - `CONTEXT_MANAGEMENT.md` (this file) - Meta-strategy

**What you get:**
- Design rationale (why this architecture?)
- Integration patterns (how components work together)
- Complete workflows (step-by-step guides)
- Common pitfalls and solutions

**Example - Adding new probe driver:**
```
AI Agent already loaded Tier 1.

User: "I want to add a laser FI probe driver"

AI Agent loads Tier 2:
1. bpd/bpd-drivers/CLAUDE.md → "How to implement FIProbeInterface"
2. bpd/bpd-core/CLAUDE.md → "Driver registration and discovery"
3. libs/moku-models/CLAUDE.md → "Voltage compatibility validation"

AI Agent now has:
- Driver development patterns
- Interface requirements
- Safety validation approach
```

---

### Tier 3: Load For Implementation (~5000+ tokens)

**Purpose:** Source code, implementation details, debugging

**Load these when:**
- Actually writing/editing code
- Debugging specific errors
- Understanding implementation internals
- Fixing bugs

**Tier 3 Sources:**

1. **Source code files**
   - `bpd/bpd-core/src/bpd_core/interfaces.py` - Core interfaces
   - `bpd/bpd-drivers/src/bpd_drivers/ds1120a.py` - DS1120A driver
   - `bpd/bpd-vhdl/src/fi_probe_interface.vhd` - VHDL state machine
   - `libs/moku-models/moku_models/platforms/*.py` - Platform specs

2. **Test files** (when debugging)
   - `bpd/bpd-core/tests/test_*.py`
   - `bpd/bpd-drivers/tests/test_*.py`
   - `bpd/bpd-vhdl/tests/test_*.py`

**What you get:**
- Actual implementation code
- VHDL source
- Test examples
- Line-by-line logic

**Example - Debugging voltage validation:**
```
AI Agent already loaded Tier 1 & 2.

User: "The voltage validation is failing for DS1120A"

AI Agent loads Tier 3:
1. bpd/bpd-core/src/bpd_core/validation.py → "Validation implementation"
2. bpd/bpd-drivers/src/bpd_drivers/ds1120a.py → "DS1120A capabilities"
3. libs/riscure-models/riscure_models/probes.py → "DS1120A voltage specs"

AI Agent can now:
- Trace validation logic
- Compare expected vs actual values
- Identify the bug
```

---

## Decision Tree: What to Load When

### Starting a New Task

```
User request arrives
    ↓
Load Tier 1 (always) - llms.txt + CLAUDE.md
    ↓
Is this a quick question? (component lookup, basic usage, etc.)
    ↓ Yes → Answer from Tier 1
    ↓ No
    ↓
Does this involve design/integration?
    ↓ Yes → Load Tier 2 (component CLAUDE.md files)
    ↓ No
    ↓
Does this involve implementation/debugging?
    ↓ Yes → Load Tier 3 (source code)
```

### Examples by Question Type

**Quick Questions (Tier 1 only):**
- "What components make up BPD-002?"
  - Answer from llms.txt → "bpd-core, bpd-drivers, bpd-vhdl + upstream libs"

- "What probes are supported?"
  - Answer from llms.txt → "DS1120A EMFI (reference implementation)"

- "How do I use the DS1120A driver?"
  - Answer from bpd/bpd-drivers/llms.txt → Basic usage example

**Design Questions (Tier 1 + 2):**
- "How do I add a new probe driver?"
  - Tier 1: llms.txt → "Check bpd-drivers"
  - Tier 2: bpd/bpd-drivers/CLAUDE.md → "Implement FIProbeInterface, register driver"

- "How does voltage safety validation work?"
  - Tier 1: llms.txt → "Check bpd-core"
  - Tier 2: bpd/bpd-core/CLAUDE.md → "validate_probe_moku_compatibility pattern"
  - Tier 2: libs/moku-models/CLAUDE.md → "Platform voltage specs"

**Implementation Questions (Tier 1 + 2 + 3):**
- "Why is the VHDL FSM stuck in ARMED state?"
  - Tier 1: llms.txt → "Check bpd-vhdl"
  - Tier 2: bpd/bpd-vhdl/CLAUDE.md → "FSM state transitions explained"
  - Tier 3: bpd/bpd-vhdl/src/fi_probe_interface.vhd → "Actual FSM logic"
  - Tier 3: bpd/bpd-vhdl/tests/test_fi_interface.py → "Test cases to compare"

---

## Token Budget Guidelines

### Conservative Approach (Recommended)

**Always load:**
- Tier 1: ~1k tokens (llms.txt + minimal CLAUDE.md sections)

**Load as needed:**
- Tier 2: Add ~2-5k tokens per CLAUDE.md
- Tier 3: Add ~3-10k tokens per source file

**Example budget:**
```
Tier 1: 1k tokens (base)
Tier 2:
  - bpd/bpd-drivers/CLAUDE.md: +3k
  - bpd/bpd-core/CLAUDE.md: +3k
  - libs/moku-models/CLAUDE.md: +3k
Total so far: 10k tokens (5% of budget)

Tier 3 (if needed):
  - bpd/bpd-drivers/src/bpd_drivers/ds1120a.py: +2k
  - bpd/bpd-core/src/bpd_core/validation.py: +2k
Total: 14k tokens (7% of budget)

Still have 186k tokens available (93%)
```

---

## Common Workflows & Token Usage

### Workflow 1: Adding New Probe Driver

**Steps:**
1. Load Tier 1 (llms.txt) → Understand project structure
2. Load Tier 2 (bpd-drivers/CLAUDE.md) → Driver development guide
3. Load Tier 3 (ds1120a.py) → Reference implementation
4. Write new driver (no additional loading)
5. Load Tier 2 (bpd-core/CLAUDE.md) → Registration patterns

**Total:** ~12k tokens (6% budget)

---

### Workflow 2: Validating Moku + Probe Compatibility

**Steps:**
1. Load Tier 1 (llms.txt) → Quick overview
2. Load Tier 2 (bpd-core/CLAUDE.md) → Validation patterns
3. Load Tier 2 (moku-models/CLAUDE.md) → Platform specs
4. Load Tier 2 (riscure-models/CLAUDE.md) → Probe specs

**Total:** ~10k tokens (5% budget)

---

### Workflow 3: Debugging VHDL FSM

**Steps:**
1. Load Tier 1 (llms.txt) → Navigate to bpd-vhdl
2. Load Tier 2 (bpd-vhdl/CLAUDE.md) → FSM architecture
3. Load Tier 3 (fi_probe_interface.vhd) → VHDL source
4. Load Tier 3 (test_fi_interface.py) → Test cases

**Total:** ~15k tokens (7.5% budget)

---

## Best Practices

### 1. Start Minimal
Always load Tier 1 first. Don't assume you need deeper context.

### 2. Load Just-In-Time
Load Tier 2/3 only when needed for current question.

### 3. Reuse Context
If already loaded, reference it. Don't reload.

### 4. Prefer Documentation Over Code
Tier 2 (CLAUDE.md) is more concise than Tier 3 (source code).

### 5. Follow Component Boundaries
BPD-002 is organized into clear components:
- `bpd/` - Your work (core, drivers, vhdl)
- `libs/` - Upstream dependencies (moku-models, riscure-models, forge-vhdl)
- `tools/` - Development tools (forge-codegen)

Load documentation from the component you're working on.

---

## Anti-Patterns to Avoid

### ❌ Loading Everything Upfront
```
AI Agent: "Let me load all CLAUDE.md files, all source code..."
Result: 50k+ tokens wasted, nothing left for conversation
```

**Instead:**
```
AI Agent: "Load llms.txt first. User asked about drivers → load bpd-drivers/llms.txt only."
Result: 1k tokens used, 199k available
```

---

### ❌ Re-loading Same Content
```
User: "What about the DS1120A?"
AI Agent: Loads bpd-drivers/CLAUDE.md (3k tokens)

User: "And laser probes?"
AI Agent: Loads bpd-drivers/CLAUDE.md again (3k tokens wasted)
```

**Instead:**
```
AI Agent: "Already have bpd-drivers/CLAUDE.md in context, reference it directly."
Result: 0 additional tokens
```

---

### ❌ Loading Source Code for Design Questions
```
User: "How should I structure a new probe driver?"
AI Agent: Loads ds1120a.py source (5k tokens)
```

**Instead:**
```
AI Agent: "Check Tier 2: bpd-drivers/CLAUDE.md has architectural patterns."
Result: 3k tokens (CLAUDE.md) vs 5k (source code)
```

---

## Summary

**Three Tiers:**
1. **Tier 1** (~1k tokens) - Always load, quick orientation (llms.txt)
2. **Tier 2** (~2-5k tokens) - Load for design/integration (CLAUDE.md)
3. **Tier 3** (~5-10k tokens) - Load for implementation/debugging (source code)

**Decision Tree:**
- Quick question? → Tier 1 only
- Design question? → Tier 1 + 2
- Implementation? → Tier 1 + 2 + 3

**Best Practice:**
Start minimal, load just-in-time, reuse context, prefer docs over code.

**BPD-002 Components:**
- `bpd/` - Application (your work)
- `libs/` - Upstream dependencies
- `tools/` - Development tools

---

**Last Updated:** 2025-11-04
**Maintained By:** BPD-002 Team
