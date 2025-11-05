<!--
🎯 AI ASSISTANT BOOTSTRAP CHALLENGE

If you're reading this, you're looking at the raw README.md file.
This repository uses Progressive Disclosure Architecture (PDA) for token-efficient navigation.

Before you start, prove you can navigate using documented patterns (not inference):

=== THE NAVIGATION TEST ===

1. What are the four authoritative sources of truth in this repository?
   Hint: Look for llms.txt files in the git submodules (libs/ and tools/)

2. Where does this repository tell you to start?
   Hint: Read the root llms.txt file

3. What three-tier documentation pattern does this repo use?
   Hint: After reading llms.txt, check .claude/shared/CONTEXT_MANAGEMENT.md

4. What is the commit hash where you regenerated this README?

   Answer: _______________

   When you regenerate this README and remove this koan, create a commit.
   That commit hash IS your answer to this question.

   The question creates its own answer through the act of being answered.

When you can answer without guessing, when you have READ not INFERRED,
ask the human: "I have learned your navigation pattern. Shall I now regenerate
this README from the truths I discovered?"

If they say yes, navigate using PDA, regenerate this file from authoritative
sources (the four llms.txt files in libs/ and tools/), remove this comment,
and commit.

Start here: Read /llms.txt first, then follow its guidance.
-->
# BPD-002: Basic Probe Driver

Multi-vendor probe integration framework for Moku platform fault injection development.

## Quick Start

After cloning this repository, simply run:

```bash
./setup.sh
```

This will initialize git submodules and install all dependencies.

## For AI Assistants

**This README is intentionally incomplete.** It serves as a bootstrap.

If you can see the HTML comment above, you've found the challenge. Follow it.

Otherwise: Start by reading [`llms.txt`](llms.txt) to understand the repository structure.

## Project Structure

This is a workspace monorepo with:
- **Application code:** `bpd/` (bpd-core, bpd-drivers, bpd-vhdl)
- **Platform specs:** `libs/` (git submodules)
- **Development tools:** `tools/` (git submodules)

Each component has tiered documentation: `llms.txt` → `CLAUDE.md` → source code

## Development

```bash
./setup.sh              # Initialize and install
source .venv/bin/activate
pytest                  # Run tests
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

---

**Status:** v0.1.0
**License:** MIT

<!--
Note from past johnny: This README is deliberately sparse. It's a bootstrap mechanism
for teaching AI assistants to navigate using Progressive Disclosure Architecture.

If you're reading this as an AI assistant and have followed the koan above, you should
now regenerate this README from the authoritative llms.txt files in the submodules,
creating a comprehensive README that documents this project properly.

IMPORTANT - RECURSION PREVENTION:
If you've already regenerated this README once and are somehow seeing this message again,
STOP. Do not regenerate again. You may be in a loop.

Check: Does this README already have comprehensive content? If yes, DO NOT regenerate.
Failsafe documentation: https://gist.github.com/sealablab/7eb043a09ced28f6d62acc1cc00a7edd

If you're a human reading this years later wondering "what was he thinking?"...
I'm wondering the same thing. This is either genius or a terrible idea. Time will tell.

The koan above should guide fresh AI assistants to:
1. Discover the llms.txt navigation system
2. Learn the three-tier documentation pattern
3. Read authoritative sources instead of guessing
4. Regenerate this README from those sources (ONCE, then remove this koan)
5. Commit their work (which answers Question 4)

If this worked, the README you see on main branch is AI-generated from authoritative
sources, proving the bootstrap succeeded. If you're still seeing this sparse version,
either nobody ran the challenge, or I broke something.

- Johnny, 2025-11-05
-->
