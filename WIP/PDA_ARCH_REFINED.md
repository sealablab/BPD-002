# Progressive Disclosure Architecture (PDA)

**Version:** 2.0
**Purpose:** Understanding the elegant flat composable architecture
**Audience:** Humans and AI agents learning this system
**Applicability:** This pattern is repository-agnostic and can be applied to any project

---

## Why PDA? (The Problem It Solves)

When building a top-level repository, you need to integrate multiple components (specifications, tools, application code) without creating a tangled mess. PDA solves this through:

1. **Flat discovery** - All submodules at one level (libs/, tools/), not nested 4 levels deep
2. **Consistent navigation** - Same 3-tier docs (llms.txt → CLAUDE.md → source) whether it's a simple Pydantic model or complex code generator
3. **Clear separation** - Interfaces (libs/) describe *what things are*, Tools (tools/) describe *how to do things*
4. **Token efficient** - AI agents load ~1k tokens to start, expand only as needed

**Result:** Add new interfaces or tools without touching existing components. The documentation pattern stays consistent across all layers.

---

## The Core Properties

### P1: Self-Contained Authoritative Components

Each component is a **self-contained authority** for its domain.

**Example: moku-models** (Platform Specs Authority)
```
libs/moku-models/
├── llms.txt           # "Moku:Go = 125MHz, Moku:Lab = 500MHz..."
├── CLAUDE.md          # "Platform integration patterns, I/O specs..."
└── moku_models/
    ├── platforms.py   # Pydantic: MOKU_GO_PLATFORM (AUTHORITATIVE)
    ├── routing.py     # I/O routing models
    └── deployment.py  # MokuConfig structures
```

- **Authority:** Clock frequencies, voltage ranges, I/O configurations
- **Standalone:** No (conceptual) dependencies on other libs
- **Importable:** Other code reads these specs, never duplicates them

**Example: riscure-models** (Probe Hardware Authority)
```
libs/riscure-models/
├── llms.txt           # "DS1120A voltage: 0-3.3V TTL..."
├── CLAUDE.md          # "Wiring safety, validation patterns..."
└── riscure_models/
    ├── probes.py      # Pydantic: DS1120A_PLATFORM (AUTHORITATIVE)
    └── validation.py  # is_voltage_compatible()
```

- **Authority:** Probe electrical specs, voltage safety
- **Standalone:** No dependencies on moku-models
- **Composable:** Can be combined with moku-models at application layer

---

### P2: Composability Without Coupling

Components are composable but don't depend on each other.

**Example: Voltage Safety Validation**
```python
# Each component knows only its domain
from moku_models import MOKU_GO_PLATFORM        # Platform authority
from riscure_models import DS1120A_PLATFORM     # Probe authority

# Libraries are independent (no imports between them)
# moku-models doesn't know riscure-models exists
# riscure-models doesn't know moku-models exists

# Your application composes them
from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility

driver = DS1120ADriver()  # Uses riscure-models specs internally
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
# → Your code orchestrates validation using both authoritative sources

# Each is authoritative for its domain, your application composes them
```

**Key insight:**
- **libs/** components don't import each other - they're standalone
- **Your application** composes them for integration validation
- Integration patterns documented in each component's CLAUDE.md

---

## The Truth Cascade (PDA in Action)

**Example: "What voltage does Moku:Go output?"**

Let's trace how PDA enables efficient, authoritative answers:

### Tier 1: Quick Navigation (~500 tokens)

```
AI loads: libs/moku-models/llms.txt

Finds (in seconds):
  # Moku:Go Platform Specifications
  - Clock: 125 MHz
  - Analog outputs: 2 channels
  - Voltage range: ±5V (10Vpp @ 50Ω)
  - Output modes: DAC (±5V), TTL (3.3V)

✓ Question answered in ~500 tokens (0.25% of budget)

If more detail needed:
  "For integration patterns, see CLAUDE.md"
```

### Tier 2: Design Context (~3k tokens, if needed)

```
AI loads: libs/moku-models/CLAUDE.md

Finds:
  - Platform comparison table (Go vs Lab vs Pro)
  - I/O routing specifications
  - Integration patterns with other hardware
  - Voltage compatibility validation examples
  - How to safely connect to external devices

✓ Design context loaded (~3k tokens, 1.5% of budget)
```

### Tier 3: Implementation (~5k tokens, only when implementing)

```
AI loads: libs/moku-models/moku_models/platforms.py

Finds:
  - MOKU_GO_PLATFORM Pydantic model (source of truth)
  - get_analog_output_by_id() method implementation
  - Complete platform specifications with validation
  - All available methods and attributes

✓ Full implementation context (~5k tokens, 2.5% of budget)
```

**Why this cascade works:**

- **moku-models** follows PDA internally (llms.txt → CLAUDE.md → source)
- **riscure-models** follows same pattern (llms.txt → CLAUDE.md → source)
- **forge-codegen** (a tool) follows same pattern despite richer internal structure
- **Your application** composes them without replicating their authority
- **AI agents** use same navigation strategy regardless of component complexity

**The pattern is reproducible:**

```bash
# Want to add a new hardware spec?
mkdir -p libs/your-hardware-models
cd libs/your-hardware-models

# 1. Create Tier 1 (quick facts)
cat > llms.txt << 'EOF'
# Your Hardware Models
Quick reference for YourDevice specifications
- Voltage: ...
- Clock: ...
For design rationale, see CLAUDE.md
EOF

# 2. Create Tier 2 (design context)
cat > CLAUDE.md << 'EOF'
# Your Hardware Models
Integration patterns, wiring safety, validation...
EOF

# 3. Implement Tier 3 (source of truth)
mkdir your_hardware_models
# Create Pydantic models...

# Done - follows same navigation pattern as moku-models and riscure-models
```

---

## The Three-Tier Documentation System (TTDS)

Every component follows the same pattern:

### Tier 1: llms.txt (~150 lines, ~500 tokens)
- Quick facts
- Core exports (table format)
- Basic usage example
- Pointers to Tier 2

**When to load:** First contact with any component

### Tier 2: CLAUDE.md (~250-600 lines, ~2-5k tokens)
- Design rationale
- Complete specifications
- Integration patterns
- Development workflows

**When to load:** Need design context or integration guidance

### Tier 3: Source Code (~variable, 5-10k tokens per file)
- Implementation details
- Pydantic models (source of truth)
- Tests

**When to load:** Implementing or debugging

**AI Agent Strategy:**
```
Quick question?  → Load Tier 1 (llms.txt)
Design question? → Load Tier 2 (CLAUDE.md)
Implementation?  → Load Tier 3 (source code)
```

---

## Never Guess, Always Trust (NGAT)

Components are **authoritative sources of truth** - never infer, always read.

```python
# ❌ BAD: AI Agent guesses
"I think Moku:Go runs at 100MHz..."          # WRONG - it's 125MHz
"The probe probably accepts 5V..."           # WRONG - DS1120A is 0-3.3V
"DS1120A likely has configurable pulse..."   # WRONG - fixed at 50ns

# ✅ GOOD: AI Agent reads authority
AI loads: libs/moku-models/llms.txt
→ "Moku:Go = 125 MHz (authoritative)"

AI loads: libs/riscure-models/llms.txt
→ "DS1120A digital_glitch = 0-3.3V TTL only"
→ "DS1120A pulse width = 50ns (FIXED, not configurable)"
```

**The principle:**
- **Never infer** specs from similar hardware
- **Always read** the authoritative component's documentation
- **Start with Tier 1** (llms.txt) for quick facts
- **Escalate to Tier 2** (CLAUDE.md) for design context
- **Load Tier 3** (source) only when implementing

---

## Token-Efficient Context Loading (TECL)

```
Quick lookup:
  Load 2-3× llms.txt (~1k tokens total)
  Budget used: 0.5%
  ✓ Answer most questions

Design work:
  Load llms.txt + 1-2× CLAUDE.md (~4k tokens)
  Budget used: 2%
  ✓ Understand integration patterns

Deep implementation:
  Load llms.txt + CLAUDE.md + source files (~10k tokens)
  Budget used: 5%
  ✓ Full context for coding

Still have 190k tokens available (95%)!
```

**Progressive loading strategy:**
1. Always start with Tier 1 (llms.txt)
2. Escalate to Tier 2 (CLAUDE.md) only if needed
3. Load Tier 3 (source) only when implementing
4. Never load everything upfront

---

## Repository Structure

```
<root>/                                        # Your repository
├── llms.txt                                   # Tier 1: Root navigation
├── CLAUDE.md                                  # Tier 2: Repository overview
├── .claude/shared/
│   └── CONTEXT_MANAGEMENT.md                  # Token optimization strategy
│
├── libs/                                      # Interfaces (git submodules)
│   ├── moku-models/                           # Platform specs (Pydantic)
│   │   ├── llms.txt                           # Tier 1: Quick ref
│   │   ├── CLAUDE.md                          # Tier 2: Integration patterns
│   │   └── moku_models/                       # Tier 3: Pydantic models
│   │
│   ├── riscure-models/                        # Probe specs (Pydantic)
│   │   ├── llms.txt                           # Tier 1: Quick ref
│   │   ├── CLAUDE.md                          # Tier 2: Safety patterns
│   │   └── riscure_models/                    # Tier 3: Pydantic models
│   │
│   └── forge-vhdl/                            # VHDL utilities
│       ├── llms.txt                           # Tier 1: Component catalog
│       └── vhdl/                              # Tier 3: VHDL packages
│
└── tools/                                     # Executable tools (git submodules)
    └── forge-codegen/                         # YAML → VHDL generator
        ├── llms.txt                           # Tier 1: Quick ref (same pattern!)
        ├── CLAUDE.md                          # Tier 2: Architecture (same pattern!)
        └── forge_codegen/                     # Tier 3: Python package
            ├── generator/                     # Code generation logic
            ├── models/                        # Internal data models
            ├── templates/                     # Jinja2 VHDL templates
            └── vhdl/                          # VHDL utilities
```

**Key Distinction:**

**libs/** = **Interfaces** (Specifications, Contracts)
- Pure Pydantic models (moku-models, riscure-models)
- VHDL component libraries (forge-vhdl)
- Zero executable logic - just specifications
- Authoritative for *what things are*
- Imported by application code

**tools/** = **Executable Tools** (Transformations, Workflows)
- Full Python packages with entry points
- Process/transform data (e.g., YAML → VHDL)
- Richer internal structure (generator/, templates/, etc.)
- Authoritative for *how to do things*
- Invoked by developers/CI systems

**Critical insight:** Both follow **same 3-tier documentation pattern** (llms.txt → CLAUDE.md → source), but tools have more complex internal structure. The navigation strategy remains identical.

---

## Design Principles

### 1. Flat Composability
- Submodules are standalone (libs/ = interfaces, tools/ = executables)
- Root repository orchestrates integration
- No nested dependencies (no submodules within submodules)
- Easy discovery (single directory level)
- Different roles, same documentation pattern

### 2. Contextual Discovery/Disclosure (Universal)
- **Same navigation pattern** for all components (libs, tools, application)
- llms.txt (quick ref) → CLAUDE.md (deep dive) → source code
- Load minimally, expand as needed
- Token budget optimization
- Pattern scales from simple interfaces to complex tools

### 3. Separation of Authority
- **libs/** authoritative for *what things are* (interfaces, specs)
- **tools/** authoritative for *how to do things* (workflows, transformations)
- Application code composes them without duplicating authority
- Never guess, always read the authoritative source

### 4. Interfaces vs Tools
- **libs/** = Interfaces (specifications, contracts, schemas)
- **tools/** = Executable Tools (transformations, workflows)
- Both are self-contained with own repos/docs/tests
- Different purposes, same contextual disclosure discipline

### 5. Context Efficiency
- Start with ~1k tokens (Tier 1: llms.txt files)
- Expand to ~4k tokens (Tier 2: CLAUDE.md files)
- Deep dive to ~10k tokens (Tier 3: source code)
- Reserve 185k+ tokens (92%+ of budget available)

---

## Git Submodule Workflow

### The Structure

PDA uses **flat composition** - all submodules at same level:

```
<root>/ (git repo)
  ├── libs/                        # Interfaces (specifications)
  │   ├── moku-models/             (git submodule)
  │   ├── riscure-models/          (git submodule)
  │   └── forge-vhdl/              (git submodule)
  │
  └── tools/                       # Executable Tools (workflows)
      └── forge-codegen/           (git submodule)
```

**Key insight:** No nested submodules - all at same level for discoverability

### The Pattern

**Modifying a submodule (e.g., moku-models in libs/):**

```bash
# 1. Navigate to submodule
cd libs/moku-models

# 2. Make changes IN THE SUBMODULE
git checkout -b feat/add-platform-spec
# ... edit code ...
git commit -m "feat: Add new platform specification"

# 3. Push THE SUBMODULE (to its own repo)
git push origin feat/add-platform-spec

# 4. Create PR in submodule repo, merge it

# 5. Return to root and update reference
cd ../..
git add libs/moku-models
git commit -m "chore: Update moku-models to include new platform"
git push
```

**Same pattern for tools/**:

```bash
cd tools/forge-codegen
git checkout -b feat/new-codegen-feature
# ... implement feature, add tests, update docs ...
git commit -m "feat: Add new code generation pattern"
git push origin feat/new-codegen-feature
# ... PR, merge ...
cd ../..
git add tools/forge-codegen
git commit -m "chore: Update forge-codegen"
git push
```

**Key rules:**
- Always commit in submodule FIRST
- Then commit submodule reference update in root repo
- Each submodule has its own repo, issues, PRs
- Flat structure = easier navigation (no nested `cd` commands)
- **libs/** and **tools/** follow same workflow, different purposes

---

## The Elegant Summary

PDA achieves:

✅ **Flat git submodule composition** (root + libs/ + tools/)
✅ **Interfaces** (libs/) + **Executable Tools** (tools/)
✅ **Contextual discovery/disclosure** - same navigation pattern across all components
✅ **3-tier documentation system** (llms.txt → CLAUDE.md → source)
✅ **Token-efficient AI context loading** (start ~1k, expand as needed)
✅ **Composability without coupling** (submodules are standalone)
✅ **Never guess, always trust** (authoritative sources of truth)
✅ **Discoverable structure** (flat hierarchy, no deep nesting)

**The magic:** Each component is independently meaningful, yet they compose elegantly through explicit patterns. AI agents navigate with minimal tokens using the **same strategy** whether exploring a simple interface (libs/) or a complex tool (tools/). Humans understand the structure intuitively. The system scales without complexity explosion.

**The pattern is reusable:** Replace `moku-models` with your domain interfaces, replace `forge-codegen` with your workflow tools, keep the same architectural principles and documentation discipline.

---

**Last Updated:** 2025-11-04
**Maintained By:** Repository maintainers
**Version:** 2.0
