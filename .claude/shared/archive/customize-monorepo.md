# Customize Monorepo

Guide the user through customizing this Moku instrument development template for their specific probe integration needs.

---

## ⚠️ PRE-FLIGHT CHECK (Run This First!)

**CRITICAL:** Before customizing, verify the monorepo is properly initialized.

**Common issue:** Users clone the repo but forget to initialize git submodules, resulting in empty submodule directories and import errors.

**Check and fix automatically:**

```bash
# 1. Check if submodules are initialized
git submodule status --recursive

# If output shows lines starting with '-' (uninitalized), fix it:
git submodule update --init --recursive

# 2. Verify workspace dependencies are installed
uv sync

# 3. Test that core libraries can be imported
python -c "from moku_models import MOKU_GO_PLATFORM; print('✓ moku_models works')"
python -c "from riscure_models import DS1120A_PLATFORM; print('✓ riscure_models works')"
```

**Expected output:**
- Submodule status shows commit hashes (not `-` prefix)
- Both import tests print ✓ messages
- No `ModuleNotFoundError` exceptions

**If imports fail after running above commands:**
- Manually install workspace members: `uv pip install -e libs/moku-models/ -e libs/riscure-models/`
- This ensures packages are available even if workspace mode has issues

**Only proceed with customization after this check passes!**

---

## 🎯 KEY INSIGHT (Read This First!)

**THIS IS A MOKU PLATFORM TEMPLATE, NOT A GENERIC FPGA TEMPLATE!**

**What users are actually doing:**
- Adding support **TO** the Moku platform **FOR** their specific probes
- Moku (via moku-models) is the **foundation**, not optional
- Riscure models are an **example** of probe integration
- Main customization: **Adding THEIR probe models** (laser, RF, etc.)

**What users are NOT doing:**
- ❌ Replacing Moku with different platform (Red Pitaya, PicoScope, etc.)
- ❌ Using this for non-Moku FPGA development
- ❌ Removing moku-models to "simplify" the template

**If someone asks about non-Moku platforms:** This template is Moku-specific. They should fork and heavily modify, or use a different template.

---

## Your Role

You are helping someone adapt this **Moku + Probe development template** for their specific hardware probes.

**Template purpose:**
- ✅ **Moku platform** (Go/Lab/Pro/Delta) - This is the CORE foundation
- ✅ **Adding probe support** to Moku (Riscure EMFI, laser probes, RF analyzers, etc.)
- ✅ **FPGA/VHDL development** for custom Moku instrument firmware

**Template components:**
- `libs/moku-models/` - **CORE** - Moku platform specifications (Go/Lab/Pro/Delta)
- `libs/riscure-models/` - Example probe specs (Riscure DS1120A EMFI probe)
- `tools/forge-codegen/` - YAML → VHDL code generator (23-type system)
- `libs/forge-vhdl/` - Reusable VHDL components (voltage utilities, clock dividers)
- `.claude/` - AI agent configurations

---

## Typical Customization Flow

```
Template (as cloned)          Customized for User's Probes
━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━━━━━

libs/moku-models/      ───►   libs/moku-models/         (KEEP - Core!)
libs/riscure-models/   ───►   libs/riscure-models/      (KEEP as reference)
                       ───►   libs/laser-models/        (ADD - Their probes!)
                       ───►   libs/rf-models/           (ADD - If needed)
tools/forge-codegen/   ───►   tools/forge-codegen/      (KEEP - VHDL gen)
libs/forge-vhdl/       ───►   libs/forge-vhdl/          (KEEP - VHDL utils)
```

**Most common pattern:** Keep everything + Add their probe models

---

## Customization Workflow

### Step 1: Understand Their Probe Integration Needs

Ask targeted questions:

**Questions to ask:**
1. **What probe(s) are you integrating with Moku?** (e.g., "Riscure EMFI", "Custom laser probe", "RF analyzer")
2. **Are you doing VHDL/FPGA development?** (Yes = keep codegen tools, No = Python-only)
3. **Do you want to keep Riscure models as reference?** (Even if using different probes, it's a good example)

**Default assumptions:**
- ✅ They ARE using Moku platform (that's the whole point!)
- ✅ They ARE adding probe support (customization is about WHICH probes)
- ✅ They likely want VHDL tools (this is FPGA development)

**Listen carefully** - Understand their probe hardware, not whether they want Moku.

---

### Step 2: Determine What to Keep

Based on their probe integration needs, recommend what to **keep**:

**ALWAYS KEEP (Core for Moku development):**
- ✅ `libs/moku-models/` - **Required** - Platform specifications (this is the foundation!)

**USUALLY KEEP (VHDL/FPGA development tools):**
- ✅ `tools/forge-codegen/` - YAML → VHDL code generator with 23-type system
- ✅ `libs/forge-vhdl/` - Reusable VHDL components (voltage conversion, clock dividers)

**DEPENDS ON PROBE TYPE:**

**If using Riscure EMFI probes:**
- ✅ Keep `libs/riscure-models/` (DS1120A/DS1140A specifications)

**If using OTHER probes (laser, RF, etc.):**
- ⚠️ **Option A (Recommended):** Keep `libs/riscure-models/` as reference example
  - Shows how to structure probe specifications
  - Example of voltage safety validation
  - Good template for creating their own probe models
- ⚠️ **Option B:** Remove `libs/riscure-models/` if they want minimal template
  - Only if they're confident in Pydantic modeling
  - They'll need to create probe models from scratch

**RARE: Python-only workflow (no VHDL/FPGA):**
- ❌ Remove `tools/forge-codegen/`
- ❌ Remove `libs/forge-vhdl/`
- ✅ Keep `libs/moku-models/` + probe models
- **Note:** This is unusual - most Moku custom instrument work involves FPGA!

---

### Step 3: Remove Unnecessary Components (If Needed)

**Most common removal:** `libs/riscure-models/` (if using different probes and want minimal template)

**Guide them through removal:**

```bash
# Remove riscure-models submodule
git rm libs/riscure-models/

# Update pyproject.toml workspace members
# Remove: "libs/riscure-models",

# Update documentation
# - Remove from llms.txt
# - Remove from CLAUDE.md "Current Architecture" section
# - Remove from .claude/manifest.json

# Sync workspace
uv sync

# Commit changes
git commit -m "chore: Remove riscure-models (using custom laser probes instead)"
```

**IMPORTANT: Don't remove these unless you know what you're doing:**
- ⛔ `libs/moku-models/` - This is the CORE! Without it, you're not developing for Moku
- ⚠️ `tools/forge-codegen/` - Only remove if doing pure Python work (no VHDL)
- ⚠️ `libs/forge-vhdl/` - Only remove if doing pure Python work (no VHDL)

**Reassure them:**
- Removing riscure-models is safe and common (if not using Riscure hardware)
- Submodules are independent - removing one doesn't break others
- They can always re-add later with `git submodule add`
- **Recommendation:** Keep it as reference even if not using Riscure probes

---

### Step 4: Add Their Custom Probe Models (MAIN CUSTOMIZATION)

**This is the key customization step!** Help them create probe specifications for their hardware.

**If using custom/different probes, guide them to create new probe models:**

**Example: Adding laser probe support**

```bash
# 1. Create new standalone repo for their probe specs
# (Guide them through creating laser-models repository)

# 2. Add as git submodule
git submodule add https://github.com/user/laser-models.git libs/laser-models/

# 3. Update pyproject.toml workspace members
# Add: "libs/laser-models",

# 4. Sync workspace
uv sync

# 5. Update documentation
# - Add to llms.txt catalog
# - Add section to CLAUDE.md
# - Add entry to .claude/manifest.json

# 6. Commit
git add .gitmodules libs/laser-models/ pyproject.toml llms.txt CLAUDE.md
git commit -m "feat: Add laser-models for optical probe support"
```

**Probe model structure (guide them):**

Create standalone repo with:
- **Pydantic models** defining probe electrical specifications
- **Voltage safety validation** (following riscure-models pattern)
- **3-tier documentation** (llms.txt → CLAUDE.md → source)
- **Port/interface definitions** (inputs, outputs, control signals)

**Point them to riscure-models as template:**
- Good example structure: `libs/riscure-models/`
- Shows voltage range validation
- Shows port specification patterns
- Has comprehensive documentation

**Other additions (less common):**
- **Additional Moku platforms** (if using unreleased/custom Moku hardware)
- **Custom VHDL components** (domain-specific beyond forge-vhdl utilities)
- **Custom code generators** (if extending beyond forge-codegen)

---

### Step 5: Help Them Fork Submodules (If Needed)

If they want to customize an existing submodule:

**Example: Forking moku-models to add custom platforms**

```bash
# 1. Fork on GitHub: github.com/sealablab/moku-models → github.com/user/moku-models

# 2. Update .gitmodules
[submodule "libs/moku-models"]
    path = libs/moku-models
    url = https://github.com/user/moku-models.git  # Their fork

# 3. Sync change
git submodule sync
cd libs/moku-models/
git remote set-url origin https://github.com/user/moku-models.git
cd ../..
```

**Remind them:**
- Forks let them customize without affecting others
- They can still pull updates from upstream
- Consider contributing useful changes back via PR

---

### Step 6: Update Documentation

Guide them to update:

**Root llms.txt:**
- Remove entries for deleted submodules
- Add entries for new submodules
- Update descriptions to match their domain

**Root CLAUDE.md:**
- Update "Current Architecture" section
- Update integration examples
- Add domain-specific patterns

**Root README.md:**
- Update project description
- Update submodule list
- Add their use-case-specific quick start

**.claude/manifest.json:**
- Update submodules list
- Mark required vs optional for their domain

---

### Step 7: Rename the Repository

Suggest renaming for clarity:

**Examples:**
- `my-laser-instrument-monorepo`
- `redpitaya-development-kit`
- `custom-fpga-toolchain`

**Update:**
- GitHub repo name
- Root README title
- Root CLAUDE.md title
- Any hardcoded references

---

### Step 8: Test Everything

Guide them through verification:

```bash
# 1. Clone fresh
git clone --recurse-submodules <their-repo> test/
cd test/

# 2. Verify submodules
git submodule status --recursive

# 3. Install dependencies
uv sync

# 4. Run tests
pytest

# 5. Check AI navigation
# Have them use Claude Code to navigate via llms.txt files
```

**If something breaks:**
- Help them debug
- Point to relevant documentation
- Suggest fixes

---

## Common Customization Scenarios

### Scenario 1: "I'm using Moku + Riscure EMFI probes" (Template as-is)

**Actions:**
- ✅ Keep everything as-is
- ✅ No customization needed!
- ✅ Just clone and start developing

**This is the reference implementation - perfect starting point.**

### Scenario 2: "I'm using Moku + Custom Laser Probes" (MOST COMMON)

**Actions:**
- ✅ Keep `libs/moku-models/` (CORE)
- ✅ Keep `tools/forge-codegen/` + `libs/forge-vhdl/` (VHDL development)
- ⚠️ Keep `libs/riscure-models/` as reference (recommended)
- ➕ Create `libs/laser-models/` (new probe specs)
- 📝 Update documentation to reflect laser probe integration

**This is the typical use case - adding NEW probe support to Moku.**

### Scenario 3: "I'm using Moku + Multiple Probe Types"

**Actions:**
- ✅ Keep `libs/moku-models/` (CORE)
- ✅ Keep `libs/riscure-models/` (if using Riscure)
- ➕ Add `libs/laser-models/` (if using laser)
- ➕ Add `libs/rf-models/` (if using RF analyzer)
- ✅ Keep all VHDL tools
- 📝 Create integration patterns in CLAUDE.md for multi-probe setups

**Multiple probe support - all probes coexist in libs/.**

### Scenario 4: "I only need Python models, no VHDL/FPGA work" (RARE)

**Actions:**
- ✅ Keep `libs/moku-models/` (CORE)
- ✅ Keep probe models (riscure or custom)
- ❌ Remove `tools/forge-codegen/`
- ❌ Remove `libs/forge-vhdl/`
- 📝 Update docs to reflect Python-only usage

**Unusual scenario - most Moku custom instrument work involves FPGA!**

### Scenario 5: "I want to extend/customize Moku platform models"

**Actions:**
- 🔀 Fork `libs/moku-models/` to your own repo
- 📝 Update `.gitmodules` to point to your fork
- ➕ Add custom platform definitions
- 🔁 Consider contributing back useful additions via PR

**For adding custom/unreleased Moku platforms or extending existing specs.**

---

## Best Practices to Recommend

**1. Document Why You Removed Things**

```bash
git commit -m "chore: Remove forge-vhdl (using SystemVerilog, not VHDL)"
```

**2. Keep the 3-Tier Documentation Pattern**

Even for their custom submodules:
- llms.txt (quick ref)
- CLAUDE.md (complete guide)
- Specialized docs (as needed)

**3. Maintain Islands of Authority**

Each submodule should be authoritative for its domain. No duplication.

**4. Test After Each Change**

Don't remove everything at once. Remove → test → commit → repeat.

**5. Consider Contributing Back**

If they create generally useful patterns, encourage PRs to the template.

---

## Encouraging Independence

**Your goal:** Help them create a **standalone customized monorepo** that:
- Fits their domain perfectly
- Follows the composable architecture pattern
- Is easy for AI agents to navigate
- Can evolve independently

**Remind them:**
- This is their fork/template - they own it
- They can change anything
- The architecture pattern is more important than specific components
- They can always reference the original template

---

## After Customization

Suggest they:

1. **Update README.md** with their use case
2. **Create issues/project board** for their work
3. **Set up CI/CD** for their specific needs
4. **Consider making their customized version public** to help others in their domain

---

## Example Dialogue

### Example 1: User with Different Probe Type

**User:** "I want to use this for Moku development with custom laser probes"

**You:**
```
Perfect! This template is designed exactly for Moku + probe integration.

Based on your laser probe needs:

KEEP (Core Moku development):
- ✅ libs/moku-models/ - Platform specs (Go/Lab/Pro/Delta)
- ✅ tools/forge-codegen/ - YAML → VHDL code generator
- ✅ libs/forge-vhdl/ - VHDL components (voltage utilities, etc.)

KEEP AS REFERENCE (Recommended):
- ⚠️ libs/riscure-models/ - Good example for structuring YOUR laser probe models
  Shows voltage safety validation, port specifications, 3-tier docs

ADD (New probe support):
- ➕ libs/laser-models/ - You'll create this for your laser probe specs
  Use riscure-models as a template for structure

OPTIONAL REMOVAL:
- You CAN remove riscure-models if you want minimal template
- But I recommend keeping it as reference!

Should I guide you through creating your laser-models submodule?
```

### Example 2: User Wants to Use Template As-Is

**User:** "I'm using Moku Go with Riscure DS1120A EMFI probe"

**You:**
```
Excellent! You don't need ANY customization - this template is already configured
for exactly your use case (Moku + Riscure EMFI).

Quick start:
1. git clone --recurse-submodules <your-repo>
2. uv sync
3. Start developing!

All components are ready:
- ✅ libs/moku-models/ - Has Moku Go specs
- ✅ libs/riscure-models/ - Has DS1120A probe specs
- ✅ tools/forge-codegen/ - Ready for YAML → VHDL generation
- ✅ libs/forge-vhdl/ - VHDL utilities available

Want me to show you the integration patterns (Moku + Riscure safety validation)?
```

### Example 3: Edge Case - Python Only

**User:** "I just need Python models for Moku platform and probe specs, no VHDL"

**You:**
```
Got it - Python-only workflow (unusual for Moku, but valid).

KEEP:
- ✅ libs/moku-models/ - Platform specifications
- ✅ libs/riscure-models/ - Probe specifications (or your custom probe models)

REMOVE (VHDL tools not needed):
- ❌ tools/forge-codegen/ - VHDL code generator
- ❌ libs/forge-vhdl/ - VHDL components

NOTE: Most Moku custom instrument development involves FPGA/VHDL work.
Are you sure you won't need code generation? If you change your mind later,
you can always add these back!

Should I guide you through removing the VHDL tools?
```

---

## Reference Documentation

Point them to:
- **CLAUDE.md:** Complete composability patterns and examples
- **TEMPLATE.md:** Step-by-step customization guide
- **.claude/manifest.json:** Programmatic submodule discovery
- **Submodule READMEs:** Each component's documentation

---

**Remember:** Your job is to guide, not dictate. Help them make informed decisions about their monorepo structure.
