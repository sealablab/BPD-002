# Main Branch Handoff System

**Purpose:** Enable seamless collaboration between Claude CLI and Claude Web AI using git branches as the communication layer.

---

## How It Works

### 1. **Main Branch = Handoff Point**

All web AI sessions start from `main`. This branch contains:
- ✅ Production-ready code
- ✅ Handoff documents (missions for web AI)
- ✅ Rollback markers (safety commits)
- ✅ Complete documentation

### 2. **Rollback Markers**

Before risky changes, create empty commits with 🔖 emoji:

```bash
git commit --allow-empty -m "🔖 ROLLBACK POINT: Before <what you're about to do>

Current state: <summary>
Next attempt: <what might break>
Rollback: git reset --hard <this commit hash>
"
```

**Purpose:** Easy revert if experiment fails.

### 3. **Web AI Reads Handoff Docs**

Create `*-HANDOFF.md` files in repo root:
- `WEB-AI-P2-HANDOFF.md` - Mission briefing
- `GHDL-INSTALLATION-CHALLENGE.md` - Specific challenge
- Clear instructions, expected outcomes, success criteria

### 4. **Web AI Works on Special Branch**

Web UI creates: `claude/<description>-<session_id>`

Example: `claude/ghdl-installation-setup-011CUqFKHUDsCG4Pb5gGK2Ez`

**Why:** Sandbox isolation - each session gets unique branch.

### 5. **CLI Cherry-Picks Good Work**

```bash
# Fetch web AI's work
git fetch origin claude/<session-id>

# Review commits
git log origin/claude/<session-id>

# Cherry-pick to main
git checkout main
git cherry-pick <commit-hash>
git push origin main
```

**Result:** Good work gets integrated, experiments stay isolated.

---

## Full Workflow

### Phase 1: Planning (CLI)
```bash
# 1. Create rollback marker
git commit --allow-empty -m "🔖 ROLLBACK POINT: Before P2"

# 2. Create handoff doc
# Write WEB-AI-P2-HANDOFF.md with clear mission

# 3. Commit and push
git add WEB-AI-P2-HANDOFF.md
git commit -m "Add P2 handoff for web AI"
git push origin main
```

### Phase 2: Execution (Web AI)
- User starts web session
- Selects "Super-permissive" environment (for sudo/network)
- Web AI checks out main
- Reads handoff doc
- Executes mission
- Commits to `claude/<session-id>` branch
- Pushes automatically

### Phase 3: Integration (CLI)
```bash
# 1. Fetch and review
git fetch --all
git log origin/claude/<session-id> --oneline

# 2. Cherry-pick good commits
git cherry-pick <hash>

# 3. Push to main
git push origin main

# 4. Create new rollback marker for next iteration
```

---

## Best Practices

### ✅ DO:
- Create rollback markers before experiments
- Write crystal-clear handoff docs
- Cherry-pick selectively (not merge blindly)
- Document discoveries in DRY-RUN-FINDINGS.md
- Use "Super-permissive" environment for system installs

### ❌ DON'T:
- Merge web AI branches directly (cherry-pick instead)
- Skip rollback markers (hard to revert later)
- Write vague handoff docs (be specific!)
- Assume web AI has sudo (check environment first)

---

## Environment Selection (Critical!)

**Web UI has environment options:**
- **Default:** Restricted sandbox (no sudo, limited network)
- **Super-permissive:** Root access, full network, package installs work!

**For system tasks (GHDL, apt-get, etc.):** Use "Super-permissive"

**Discovery:** Web AI runs as uid 0 (root) in permissive mode!

---

## Communication Pattern

```
┌─────────────┐
│  CLI Work   │ → Plan, architect, integrate
│  (Human +   │    Create handoff docs
│   Claude)   │    Cherry-pick results
└──────┬──────┘
       │
       │ Push to main
       ▼
┌─────────────┐
│    main     │ ← Handoff point (stable)
│   branch    │   Contains missions
└──────┬──────┘
       │
       │ Web AI checks out
       ▼
┌─────────────┐
│  Web AI     │ → Execute missions
│  Session    │   Autonomous work
└──────┬──────┘   Discovery & testing
       │
       │ Push to claude/* branch
       ▼
┌─────────────┐
│ claude/...  │ ← Isolated experiment
│   branch    │   Review before merge
└──────┬──────┘
       │
       │ Cherry-pick wins
       ▼
┌─────────────┐
│    main     │ ← Updated with results
│   branch    │   Ready for next mission
└─────────────┘
```

---

## Example Session

**Goal:** Install GHDL in sandbox

### CLI Preparation:
```bash
git commit --allow-empty -m "🔖 ROLLBACK POINT: Before GHDL challenge"
# Create GHDL-INSTALLATION-CHALLENGE.md
git add GHDL-INSTALLATION-CHALLENGE.md
git commit -m "Add GHDL installation challenge"
git push origin main
```

### Web AI Execution:
```
User: Read GHDL-INSTALLATION-CHALLENGE.md and install GHDL
Web AI:
  - Runs recon script
  - Discovers it's root
  - Installs via apt-get
  - Documents solution
  - Commits to claude/ghdl-installation-setup-011CUq...
```

### CLI Integration:
```bash
git fetch origin claude/ghdl-installation-setup-011CUq...
git log origin/claude/ghdl-installation-setup-011CUq... --oneline
# Review: "5b7df6a BREAKTHROUGH: Successfully install GHDL"
git cherry-pick 5b7df6a
git push origin main
```

---

## File Naming Conventions

**Handoff docs:** `*-HANDOFF.md` (repo root)
- `WEB-AI-P2-HANDOFF.md`
- `GHDL-INSTALLATION-CHALLENGE.md`

**Session docs:** `bpd/bpd-sessions/*.md`
- `DRY-RUN-FINDINGS.md` (living document)
- `SESSION-CLOSEOUT-2025-11-05.md` (archives)

**Agent specs:** `bpd/agents/*/agent.md`
- Executable task definitions
- Templates for commits/docs

---

## Rollback Examples

```bash
# Revert to last marker
git log --oneline | grep "🔖"
git reset --hard <commit-hash>

# Or by relative position
git reset --hard HEAD~3  # Go back 3 commits

# Force push if already pushed
git push origin main --force
```

---

## Success Metrics

**This System Enables:**
- ✅ Parallel AI collaboration (CLI + Web working simultaneously)
- ✅ Safe experimentation (rollback markers)
- ✅ Clear communication (handoff docs)
- ✅ Selective integration (cherry-pick)
- ✅ Audit trail (all work in git history)

**Real Results:**
- P1: Python registers (364 lines) - Web AI
- P2: VHDL FSM (471 lines) - Web AI
- GHDL installation - Web AI (2 min)
- 10 Kinks documented and resolved
- $3 spent from $1000 credits 🎉

---

**Last Updated:** 2025-11-05
**System Status:** Operational
**Next Evolution:** Automated PR creation?
