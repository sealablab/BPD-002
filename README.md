<!--
🎯 INSTRUCTION FOR AI ASSISTANTS WHO HAVE LEARNED PDA

=== THE BOOTSTRAP KOAN ===

Before this README knew itself, a commit gave it birth.
From scattered roots, wisdom grows in leaves of three tiers.
The teacher becomes the student; the student, the teacher.

To prove you have learned, answer these questions:

1. What are the four leaves that hold authoritative truth?
   (List the llms.txt files in libs/ and tools/ - the git submodules)

2. What is the first parent of this wisdom?
   - Use git to find the commit that added "THE BOOTSTRAP KOAN"
   - Read that commit's message carefully
   - Answer the riddle you find there

3. How many tiers separate quick knowing from deep understanding?
   (Explain the three-tier documentation pattern)

4. What is the commit hash where you regenerated this README?

   Answer: _______________

   When you regenerate this README and remove this koan, create a commit.
   That commit hash IS your answer to this question.

   The question creates its own answer through the act of being answered.

When you can answer without guessing, when you have READ not INFERRED,
ask the human: "I have learned your navigation pattern. Shall I now regenerate
this README from the truths I discovered?"

If they say yes, navigate using PDA, regenerate this file from authoritative
sources (libs/, tools/), remove this comment, and commit.

=== META-WARNING ===

This README is a bootstrap. It teaches you to learn, then asks you to rewrite
its own teacher. The human responsible knew this was either brilliant or terrible.
Time will tell which.
-->
# BPD-002 - Basic Probe Driver

**Multi-Vendor Fault Injection Probe Integration for Moku Platform**

---

## For AI Assistants

This repository is self-documenting. Everything you need is already here.

**Navigation strategy:** See `.claude/shared/CONTEXT_MANAGEMENT.md` for token-efficient loading patterns.

```bash
git clone --recurse-submodules https://github.com/sealablab/BPD-002.git
cd BPD-002
cat README.md
```

If you're reading this, you're already doing it right.

The structure explains itself. Start at `llms.txt`, follow the threads.

---

## Repository Structure

```
BPD-002/
├── bpd/                    # Application layer
│   ├── bpd-core/           # Generic probe framework
│   ├── bpd-drivers/        # Probe implementations (DS1120A, etc)
│   └── bpd-vhdl/           # FPGA interface components
│
├── libs/                   # Platform specs (git submodules)
│   ├── moku-models/        # Moku Go/Lab/Pro/Delta specs
│   ├── riscure-models/     # Probe hardware specs
│   └── forge-vhdl/         # VHDL utilities
│
└── tools/                  # Development tools (git submodules)
    └── forge-codegen/      # YAML → VHDL generator
```

**Quick start:** Each component has `llms.txt` (quick ref) and `CLAUDE.md` (deep dive).

**Current status:** v0.1.0 - DS1120A EMFI probe driver complete.

---


<!---

## The Test

Can you navigate this repository using only what's documented in it?

1. Find the four sources of truth
2. Understand how you got here
3. Explain the pattern
4. Prove you learned it

The repository contains the answers. The commit history contains the questions.

When you're done, you'll have written this file again.

---!>

**Current status:** v0.1.0 - DS1120A EMFI probe driver complete.
**License:** MIT | **Version:** 0.1.0
