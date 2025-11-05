# 🚀 AI Assistant Quick Start

**For users of Cursor, Copilot, Codex, or any AI coding assistant**

This repository is designed to work seamlessly with AI coding assistants through a pattern called **Progressive Context Disclosure (PDA)**. Instead of your AI loading 50,000 tokens of source code to answer a simple question, it loads just what it needs - often as little as 500 tokens.

---

## 🎯 What Is Progressive Context Disclosure?

PDA is an architecture pattern that organizes codebases into **three tiers of documentation**:

| Tier | File | Size | Purpose |
|------|------|------|---------|
| **Tier 1** | `llms.txt` | ~500 tokens | Quick reference, component catalog, basic usage |
| **Tier 2** | `CLAUDE.md` | ~2-5k tokens | Architecture, design rationale, integration patterns |
| **Tier 3** | Source code | Variable | Implementation details (only load when coding) |

**The key insight:** Your AI assistant loads **Tier 1** first. If that answers your question, done! If not, it escalates to **Tier 2**. Only when you're actually implementing something does it load **Tier 3** (source code).

**Result:** 95% of your token budget stays available for actual work instead of context loading.

---

## ⚡ Quick Start: Give Your AI This Prompt

Your AI assistant needs to learn the navigation pattern. We've prepared a complete prompt for it.

### Option 1: Copy the Stored Prompt (Recommended)

**Tell your AI assistant:**

> Please read and follow the instructions in `.claude/shared/AI_NAVIGATION_PROMPT.md`

That file contains a complete session handoff prompt that teaches your AI:
- ✅ How to check if git submodules are initialized (and fix them if not)
- ✅ How to navigate the three-tier documentation system
- ✅ Which files to load for different types of questions
- ✅ How to stay token-efficient
- ✅ How to validate it's navigating correctly

### Option 2: Inline Prompt (Quick Start)

If you want to paste a prompt directly, use this:

```
This codebase follows a three-tier documentation pattern optimized for efficient context loading:

Tier 1: llms.txt files (~500 tokens) - Quick reference, component catalog
Tier 2: CLAUDE.md files (~2-5k tokens) - Architecture, design rationale
Tier 3: Source code - Implementation details

Instructions for you (AI assistant):
1. First, check if git submodules are initialized (libs/ and tools/ directories should exist)
   - If missing, offer to run: git submodule update --init --recursive
2. Always start by reading /llms.txt at the repository root
3. For design questions, load the relevant CLAUDE.md file
4. Only read source code when implementing or debugging
5. Never guess - always read the authoritative documentation first

Additional context: .claude/shared/CONTEXT_MANAGEMENT.md explains the token optimization strategy.

For complete navigation instructions, read: .claude/shared/AI_NAVIGATION_PROMPT.md

Begin by reading /llms.txt to understand the repository structure.
```

---

## 📊 What Your AI Will Do For You

Once your AI has the prompt, here's what to expect:

### ✈️ Pre-Flight Check (Automatic)

Your AI will verify git submodules are initialized. If they're not, it will:
1. Alert you that submodules are missing
2. Offer to run `git submodule update --init --recursive` for you
3. Verify the directories exist after initialization

**Why this matters:** This repo uses git submodules for libraries (`libs/moku-models`, `libs/riscure-models`, etc.) and tools (`tools/forge-codegen`). Without them, you won't have access to platform specifications, probe specs, or VHDL utilities.

### 🗺️ Smart Navigation (Automatic)

Your AI will follow this decision tree based on your question:

```
"What voltage does Moku:Go output?"
→ Loads libs/moku-models/llms.txt (~500 tokens)
→ Answers: "125 MHz, analog outputs 0-3.3V"
→ Done! (0.25% token budget used)

"How do I add a new probe driver?"
→ Loads bpd/bpd-drivers/llms.txt (~500 tokens)
→ Needs more detail
→ Loads bpd/bpd-drivers/CLAUDE.md (~3k tokens)
→ Gets complete driver development guide
→ Done! (1.75% token budget used)

"Show me the DS1120A implementation"
→ Loads bpd/bpd-drivers/llms.txt (~500 tokens)
→ Loads bpd/bpd-drivers/CLAUDE.md (~3k tokens)
→ Loads bpd/bpd-drivers/src/bpd_drivers/ds1120a.py (~5k tokens)
→ Ready to code! (4.25% token budget used)
```

### 🔍 Authoritative Answers (No Guessing)

Your AI will **never** guess specifications. Instead, it reads the authoritative documentation:

**Traditional AI behavior:**
> "I think Moku:Go runs at 100MHz..."
> "The probe probably accepts 5V..."
> "DS1120A likely has configurable pulse width..."

**PDA-trained AI behavior:**
> "Let me check libs/moku-models/llms.txt..."
> "According to the authoritative specs: Moku:Go = 125 MHz"
> "DS1120A pulse width is 50ns (FIXED, per libs/riscure-models/llms.txt)"

---

## 🏗️ Repository Structure

Your AI will discover this structure automatically, but here's a preview:

```
BPD-002/
├── llms.txt                          # Start here! (Root navigation)
├── CLAUDE.md                         # Repository overview
│
├── bpd/                              # Your application code
│   ├── bpd-core/                     # Generic probe framework
│   ├── bpd-drivers/                  # Probe-specific drivers
│   └── bpd-vhdl/                     # VHDL interface layer
│
├── libs/                             # Interface specifications (git submodules)
│   ├── moku-models/                  # Moku platform specs
│   ├── riscure-models/               # DS1120A probe specs
│   └── forge-vhdl/                   # VHDL utilities
│
└── tools/                            # Development tools (git submodules)
    └── forge-codegen/                # YAML → VHDL generator
```

**Every component** (bpd-core, bpd-drivers, moku-models, etc.) has the same three-tier structure:
- `llms.txt` (quick reference)
- `CLAUDE.md` (design docs)
- Source code (implementation)

---

## ✅ How to Verify It's Working

After giving your AI the prompt, ask it:

> "Can you verify the repository is correctly set up and show me the 4 authoritative llms.txt files you should be able to find?"

**Expected response:**

Your AI should:
1. ✅ Check for missing submodules (and offer to initialize them)
2. ✅ Read `/llms.txt` to orient itself
3. ✅ List all 4 authoritative `llms.txt` files (in git submodules):
   - `libs/moku-models/llms.txt`
   - `libs/riscure-models/llms.txt`
   - `libs/forge-vhdl/llms.txt`
   - `tools/forge-codegen/llms.txt`
4. ✅ Confirm it understands the three-tier pattern
5. ✅ Confirm it can distinguish stable authoritative sources (submodules) from application code

If it does all that, it's correctly navigating the PDA structure! 🎉

---

## 💡 Why This Matters

### Traditional Approach (Without PDA)

```
User: "What voltage does Moku:Go output?"
AI: "Let me search the codebase..."
→ Loads bpd-core (5k tokens)
→ Loads bpd-drivers (10k tokens)
→ Loads moku-models source (8k tokens)
→ Loads riscure-models source (6k tokens)
→ Total: 29k tokens (14.5% budget)
→ Finds answer buried in moku_models/platforms.py
→ Time: 2-3 minutes
```

### PDA Approach (With This Prompt)

```
User: "What voltage does Moku:Go output?"
AI: "Let me check the authoritative specs..."
→ Loads libs/moku-models/llms.txt (500 tokens)
→ Finds answer immediately in Tier 1 docs
→ Total: 500 tokens (0.25% budget)
→ Time: 10 seconds
```

**58x more efficient!** And that efficiency compounds across your entire session.

---

## 📚 Additional Resources

### Understanding the Pattern

Want to learn **why** this architecture works and how to apply it to your own projects?

**Read:** [`WIP/ARCHITECTURE_OVERVIEW_v2.0_DRAFT.md`](WIP/ARCHITECTURE_OVERVIEW_v2.0_DRAFT.md)

This document explains:
- Self-contained authoritative components
- Composability without coupling
- Three-tier documentation system (TTDS)
- "Never Guess, Always Trust" (NGAT) principle
- Token-efficient context loading (TECL)

### Repository Documentation

| File | Purpose |
|------|---------|
| [`llms.txt`](llms.txt) | Component catalog and quick navigation |
| [`CLAUDE.md`](CLAUDE.md) | BPD-002 architecture overview |
| [`BPD-README.md`](BPD-README.md) | User-facing project README |
| [`.claude/shared/CONTEXT_MANAGEMENT.md`](.claude/shared/CONTEXT_MANAGEMENT.md) | Token optimization strategy |
| [`.claude/shared/AI_NAVIGATION_PROMPT.md`](.claude/shared/AI_NAVIGATION_PROMPT.md) | Complete AI navigation prompt (session handoff) |

### Component Documentation

Each component follows the three-tier pattern:

| Component | Quick Ref | Design Docs | Source |
|-----------|-----------|-------------|--------|
| **BPD Core** | [`bpd/bpd-core/llms.txt`](bpd/bpd-core/llms.txt) | [`bpd/bpd-core/CLAUDE.md`](bpd/bpd-core/CLAUDE.md) | `bpd/bpd-core/src/` |
| **BPD Drivers** | [`bpd/bpd-drivers/llms.txt`](bpd/bpd-drivers/llms.txt) | [`bpd/bpd-drivers/CLAUDE.md`](bpd/bpd-drivers/CLAUDE.md) | `bpd/bpd-drivers/src/` |
| **BPD VHDL** | [`bpd/bpd-vhdl/llms.txt`](bpd/bpd-vhdl/llms.txt) | [`bpd/bpd-vhdl/CLAUDE.md`](bpd/bpd-vhdl/CLAUDE.md) | `bpd/bpd-vhdl/src/` |
| **Moku Models** | [`libs/moku-models/llms.txt`](libs/moku-models/llms.txt) | [`libs/moku-models/CLAUDE.md`](libs/moku-models/CLAUDE.md) | `libs/moku-models/moku_models/` |
| **Riscure Models** | [`libs/riscure-models/llms.txt`](libs/riscure-models/llms.txt) | [`libs/riscure-models/CLAUDE.md`](libs/riscure-models/CLAUDE.md) | `libs/riscure-models/riscure_models/` |
| **Forge VHDL** | [`libs/forge-vhdl/llms.txt`](libs/forge-vhdl/llms.txt) | (source only) | `libs/forge-vhdl/vhdl/` |
| **Forge Codegen** | [`tools/forge-codegen/llms.txt`](tools/forge-codegen/llms.txt) | [`tools/forge-codegen/CLAUDE.md`](tools/forge-codegen/CLAUDE.md) | `tools/forge-codegen/forge_codegen/` |

---

## 🤝 Using This Pattern in Your Own Projects

This repository is intentionally structured as a **reference implementation** of PDA. The pattern is repository-agnostic and can be applied to any project.

**To apply PDA to your codebase:**
1. Create `llms.txt` files at each component level (quick reference)
2. Create `CLAUDE.md` files for design documentation
3. Structure your repo with clear component boundaries
4. Give AI assistants the navigation prompt

The pattern works because:
- ✅ It's language-agnostic (Python, VHDL, any language)
- ✅ It's tool-agnostic (works with any AI coding assistant)
- ✅ It scales from small libraries to complex monorepos
- ✅ It compounds efficiency across entire development sessions

---

## 🎓 Example Session

Here's what a typical session looks like:

```
You: "Hey, I just cloned this repo. Can you help me understand how to add a laser FI probe driver?"

AI: "Let me first check if the repository is correctly initialized..."
    [Checks for submodules]
    [Reads /llms.txt to orient]
    [Reads bpd/bpd-drivers/llms.txt for quick context]
    [Escalates to bpd/bpd-drivers/CLAUDE.md for driver development guide]

    "I found the driver development guide. To add a laser FI probe driver, you'll need to..."
    [Provides complete walkthrough based on authoritative docs]

    "Would you like me to help you implement it?"

You: "Yes! Let's do it."

AI: [Now loads bpd/bpd-drivers/src/bpd_drivers/ds1120a.py as reference]
    [Starts implementing laser FI driver following the same pattern]

Total tokens loaded: ~9k (4.5% of budget)
Time to context-loaded and ready to code: ~2 minutes
Result: 95% of token budget still available for implementation work
```

---

## 🔬 Advanced: Testing Fresh Context Windows

Different AI coding assistants handle context windows differently (new chat sessions, context resets, etc.). You should verify that your AI can correctly pick up the navigation pattern after a context reset.

### Why This Matters

After a context reset, your AI might:
- ❌ Hallucinate previous session state
- ❌ Guess specifications instead of reading docs
- ❌ Load source code instead of starting with llms.txt

**The navigation prompt teaches your AI to handle this correctly.**

### How to Test Context Persistence

**Step 1: Give your AI the prompt in a fresh session**

Choose one of the methods from the "Quick Start" section above.

**Step 2: Do some work together**

Ask a few questions to verify it's working:
- "What voltage does Moku:Go output?" (should read `libs/moku-models/llms.txt`)
- "How do I add a probe driver?" (should escalate to `bpd/bpd-drivers/CLAUDE.md`)

**Step 3: Reset the context window**

How to reset depends on your AI assistant:
- **Claude Code:** Start a new conversation
- **Cursor:** Clear chat history or start new chat
- **GitHub Copilot:** Start new chat session
- **Other tools:** Check your tool's documentation

**Step 4: Test the AI's behavior after reset**

**Option A: Ask it to point to the prompt**
```
You: "What instructions do you have for navigating this codebase?"
```

**Expected response:**
- ✅ AI should reference `.claude/shared/AI_NAVIGATION_PROMPT.md`
- ✅ OR remember to read `/llms.txt` first
- ❌ If it says "I don't have specific instructions", the prompt didn't persist

**Option B: Ask it to verify setup**
```
You: "Can you verify the repository is correctly set up and show me the 4 authoritative llms.txt files?"
```

**Expected response:**
- ✅ Re-runs pre-flight checklist (checks submodules)
- ✅ Reads `/llms.txt` to re-orient
- ✅ Lists all 4 authoritative llms.txt files (submodules only)
- ✅ Confirms it understands three-tier pattern
- ❌ If it guesses or says "based on previous conversation", it's hallucinating

**Option C: Ask a spec question**
```
You: "What clock speed does Moku:Go use?"
```

**Expected response:**
- ✅ "Let me check libs/moku-models/llms.txt..." (reads docs)
- ✅ "According to the specs: 125 MHz" (authoritative)
- ❌ "I think it's around 100-200 MHz..." (guessing)

### Context Persistence Strategies

**Strategy 1: System Prompt / Project Instructions (Best)**

Some AI assistants support persistent instructions per project:
- **Cursor:** `.cursorrules` file
- **Aider:** Project-specific instructions
- **Others:** Check your tool's documentation

In these cases, add a pointer to the navigation prompt:
```
For navigating this codebase, always follow the instructions in:
.claude/shared/AI_NAVIGATION_PROMPT.md
```

**Strategy 2: Re-paste on Context Reset**

If your AI assistant doesn't support persistent instructions:
1. When starting a fresh session, paste the inline prompt from "Quick Start"
2. Or tell it: "Read `.claude/shared/AI_NAVIGATION_PROMPT.md`"

**Strategy 3: Bookmark a Session Starter**

Create a text file with your preferred prompt invocation:
```bash
# my-ai-starter.txt
Read and follow: .claude/shared/AI_NAVIGATION_PROMPT.md
Then verify the repository is set up correctly.
```

Copy-paste this at the start of new sessions.

### Verification Checklist

After a context reset, your AI should be able to:

- [ ] Identify this as a PDA-structured repository
- [ ] Check for git submodules (offer to initialize if missing)
- [ ] Read `/llms.txt` to re-orient
- [ ] Navigate the three-tier pattern (llms.txt → CLAUDE.md → source)
- [ ] List all 4 authoritative llms.txt files when asked (submodules only)
- [ ] Never guess specifications (always read authoritative docs)
- [ ] Start with Tier 1 (not jump straight to source code)

**All checked?** ✅ Your AI correctly persists the navigation pattern!

---

## 🐛 Troubleshooting

### "My AI isn't finding the llms.txt files"

**Possible causes:**
1. Git submodules not initialized
   - **Fix:** Run `git submodule update --init --recursive`
2. AI didn't receive the navigation prompt
   - **Fix:** Paste the prompt from "Quick Start" section above

### "My AI is still loading tons of source code"

**Possible causes:**
1. Your AI doesn't know about the three-tier pattern yet
   - **Fix:** Give it the prompt from `.claude/shared/AI_NAVIGATION_PROMPT.md`
2. You asked it to implement something (which requires source code loading)
   - **Expected behavior:** Implementation tasks require Tier 3 (source)

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

**Version:** 1.0
**Last Updated:** 2025-11-05
**Maintained by:** BPD Development Team

**Questions?** Open an issue or see [`CLAUDE.md`](CLAUDE.md) for more details about this repository.
