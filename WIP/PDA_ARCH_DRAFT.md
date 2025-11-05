# Composable Architecture Overview 
**Version:** 2.0
**Purpose:** Understanding the elegant flat composable architecture
**Audience:** Humans and AI agents learning this system
**Applicability:** This pattern is repository-agnostic and can be applied to any project


## P1: Self-Contained Authoritative Components

Each component is a **self-contained authority** for its domain:
For example:
**moku-models** (Platform Specs Authority)
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
- **Standalone** - no (conceptual) dependencies



## P2: Composability Without Coupling

Components are composable but don't depend on each other:
Again, using the moku and riscure models as an example:
```python
# Each component knows only its domain
from moku_models import MOKU_GO_PLATFORM
from riscure_models import DS1120A_PLATFORM

# Libraries are independent (no imports between them)

# Compose at framework layer for cross-validation
from bpd_drivers import DS1120ADriver

driver = DS1120ADriver()  # Uses riscure-models specs
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
# → bpd-core orchestrates validation using both authoritative sources

# Each is authoritative for its domain, bpd-core composes them
```

**Key insight:**
- **libs/** components don't import each other - they're standalone
- **bpd/bpd-core/** composes them for integration validation
- Integration patterns documented in component CLAUDE.md files


## The Architecture (PDA)

This architecture demonstrates a **flat, composable design** with **self-contained authoritative submodules** that integrate through explicit patterns, supported by a **contextual discovery/disclosure approach** optimized for token-efficient AI context loading.


**Why this design works for composition:**

When building a top-level repository, you need to integrate multiple components (specifications, tools, application code) without creating a tangled mess. This pattern solves that by:

1. **Flat discovery** - All submodules at one level (libs/, tools/) not nested 4 levels deep
2. **Consistent navigation** - Same 3-tier docs (llms.txt → CLAUDE.md → source) whether it's a simple Pydantic model or complex code generator
3. **Clear separation** - Interfaces (libs/) describe *what things are*, Tools (tools/) describe *how to do things*, your application composes them
4. **Token efficient** - AI agents load ~1k tokens to start, expand only as needed

**Result:** You can add new interfaces (hardware specs, data models) or new tools (generators, validators) without touching existing components. Your application imports the interfaces, invokes the tools, and the documentation pattern stays consistent across all layers.

---

## The results:  Truth Cascades up.  (PDA in Action)

**Example: How would an AI agent answer "What voltage does Moku:Go output?"**

Let's trace how PDA enables efficient, authoritative answers using real repos:


# Tiers: 
Now that we have seen it in use, lets explain how this is accomplished:
 Tier1:  Quick Navigation (`llms.txt`)
 Tier2:  Design Context CLAUDE.MD (`CLAUDE.md`)
 Tier3:  Implementation details (source code)

### Tier2: Design Context (`CLAUDE.md`)

```
AI loads: libs/moku-models/CLAUDE.md (~3k tokens)

Finds:
  - Platform comparison table
  - I/O routing specifications
  - Integration patterns with other hardware
  - How to validate voltage compatibility
```

### Tier 3: Source code : (Implementation only when implementing)

```
AI loads: libs/moku-models/moku_models/platforms.py (~5k tokens)

Finds:
  - MOKU_GO_PLATFORM Pydantic model (source of truth)
  - get_analog_output_by_id() method
  - Complete platform specifications
```

**Why this works:**

- **moku-models** repo follows PDA internally (llms.txt → CLAUDE.md → source)
- **riscure-models** repo follows same pattern (llms.txt → CLAUDE.md → source)
- **Your application** composes them without replicating their authority
- **AI agent** uses same navigation strategy regardless of repo complexity

**The pattern is reproducible:**


---



---

## 3. Monorepo structure (top)

```
<root>/                                        # Repository root
├── llms.txt                                   # Tier 1: Root navigation
├── CLAUDE.md                                  # Tier 2: Repository overview
├── .claude/shared/
│   └── CONTEXT_MANAGEMENT.md                  # Token optimization strategy
│
├── libs/                                      # Interfaces (git submodules)
│   ├── moku-models/                           # Platform specs (Pydantic models)
│   │   ├── llms.txt                           # Tier 1: Platform quick ref
│   │   ├── CLAUDE.md                          # Tier 2: Integration patterns
│   │   └── moku_models/                       # Pure Pydantic models
│   │
│   ├── riscure-models/                        # Probe hardware specs (Pydantic models)
│   │   ├── llms.txt                           # Tier 1: Probe specs
│   │   ├── CLAUDE.md                          # Tier 2: Safety patterns
│   │   └── riscure_models/                    # Pure Pydantic models
│   │
│   └── forge-vhdl/                            # Reusable VHDL utilities
│       ├── llms.txt                           # Tier 1: Component catalog
│       └── vhdl/                              # VHDL packages (no Python)
│
└── tools/                                     # Executable tools (git submodules)
    └── forge-codegen/                         # YAML → VHDL generator
        ├── llms.txt                           # Tier 1: Quick ref (same pattern!)
        ├── CLAUDE.md                          # Tier 2: Architecture (same pattern!)
        └── forge_codegen/                     # Python package
            ├── generator/                     # Code generation logic
            ├── models/                        # Internal data models
            ├── templates/                     # Jinja2 VHDL templates
            ├── vhdl/                          # VHDL utilities
            └── basic_serialized_datatypes/    # Type system helpers
```

**Key Distinction:**

**libs/** = **Interfaces** (Specifications, Contracts)
- Pure Pydantic models (moku-models, riscure-models)

## 3) TTDS: Three-Tier Documentation System

Every authoritative component follows the pattern:

**Tier 1: llms.txt** (~150 lines, ~500 tokens)
- Quick facts
- Core exports (table format)
- Basic usage example
- Pointers to Tier 2

**Tier 2: CLAUDE.md** (~250-600 lines, ~2-5k tokens)
- Design rationale
- Complete specifications
- Integration patterns
- Development workflows

**Tier 3: Source Code** (~variable, 5-10k tokens per file)
- Implementation details
- Pydantic models
- Tests

**AI Agent Strategy:**
```
Quick question? → Load Tier 1 (llms.txt)
Design question? → Load Tier 2 (CLAUDE.md)
Implementation? → Load Tier 3 (source code)
```

### 4) NGAT: (Never Guess, Always Trust)

Components are **authoritative sources of truth**:

```python
# ❌ BAD: AI Agent guesses
"I think Moku:Go runs at 100MHz..."
"The probe probably accepts 5V..."
"DS1120A likely has configurable pulse width..."

# ✅ GOOD: AI Agent reads authority
AI loads: libs/moku-models/llms.txt
→ "Moku:Go = 125 MHz (authoritative)"

AI loads: libs/riscure-models/llms.txt
→ "DS1120A digital_glitch = 0-3.3V TTL only"
→ "DS1120A pulse width = 50ns (FIXED, not configurable)"

AI loads: bpd/bpd-core/llms.txt
→ "FIProbeInterface protocol defines: arm(), trigger(), disarm()"
```

**The principle:**
- **Never infer** specs from similar hardware
- **Always read** the authoritative component's documentation
- **Start with Tier 1** (llms.txt) for quick facts
- **Escalate to Tier 2** (CLAUDE.md) for design context

###  5) TECL: Token-Efficient Context Loading

```
Quick lookup:
  Load 3× llms.txt (450 lines total, ~1k tokens)
  Budget used: 0.5%

Design work:
  Load llms.txt + MODELS_INDEX.md + 1× CLAUDE.md (~4k tokens)
  Budget used: 2%

Deep implementation:
  Load llms.txt + CLAUDE.md + source files (~10k tokens)
  Budget used: 5%

Still have 190k tokens available (95%)!
```

---
### Library Layer (libs/) - Authoritative Submodules
```
libs/
├── moku-models/                    # Platform specs (git submodule)
│   ├── llms.txt                    # Tier 1: Platform quick ref
│   ├── CLAUDE.md                   # Tier 2: Integration patterns
│   └── moku_models/                # Tier 3: Pydantic models
│
├── riscure-models/                 # Probe hardware (git submodule)
│   ├── llms.txt                    # Tier 1: Probe specs
│   ├── CLAUDE.md                   # Tier 2: Safety patterns
│   └── riscure_models/             # Tier 3: Pydantic models
│
└── forge-vhdl/                     # VHDL utilities (git submodule)
    ├── llms.txt                    # Tier 1: Component catalog
    └── vhdl/                       # Tier 3: VHDL packages
```

---

## 5. Design Principles

### 1. Flat Composability
- Submodules are standalone (libs/ = interfaces, tools/ = executables)
- Root repository orchestrates integration
- No nested dependencies
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

---

