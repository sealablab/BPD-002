# Next Session Plan

**⚠️ BEFORE YOU START: Create a session branch**

```bash
# 1. Make sure you're on main and up to date
git checkout main
git pull

# 2. Create a dated session branch (use today's date)
git checkout -b session/YYYY-MM-DD-short-description

# Example:
# git checkout -b session/2025-11-06-vhdl-integration
```

**After creating your branch, copy this file to a dated version:**
```bash
cp bpd/bpd-sessions/NEXT-SESSION.md bpd/bpd-sessions/$(date +%Y-%m-%d)-your-description.md
git add bpd/bpd-sessions/$(date +%Y-%m-%d)-your-description.md
git commit -m "Add session plan: $(date +%Y-%m-%d)"
```

---

## Session Plan: [DATE] - [SHORT DESCRIPTION]

**Branch:** `session/YYYY-MM-DD-description`
**Focus:** [What's the main goal?]
**Status:** 🟡 Planning

---

## Session Goals

### 🎯 Primary Objectives

1. **[First Major Goal]**
   - [ ] Specific task 1
   - [ ] Specific task 2
   - [ ] Specific task 3

2. **[Second Major Goal]**
   - [ ] Specific task 1
   - [ ] Specific task 2

3. **[Third Major Goal]**
   - [ ] Specific task 1
   - [ ] Specific task 2

### 🔧 Secondary Objectives (Time Permitting)

4. **[Nice-to-have Goal]**
   - [ ] Optional task 1
   - [ ] Optional task 2

5. **[Documentation/Cleanup]**
   - [ ] Update relevant docs
   - [ ] Clean up any technical debt

---

## Technical Context

### Current State
- ✅ What's already done
- ✅ What's working
- ⚠️ **Gap:** What's missing
- ⚠️ **Gap:** What needs work

### Key Files to Touch
- `path/to/file1.py` - Purpose
- `path/to/file2.vhd` - Purpose
- `path/to/test.py` - Purpose

### Architecture Notes
```
[Optional diagram or flow description]
Component A
    ↓ does something
Component B
    ↓ outputs to
Component C
```

---

## Success Criteria

**Minimum Viable Session:**
- [ ] Core functionality works
- [ ] At least N tests passing
- [ ] No critical errors

**Stretch Goals:**
- [ ] Full test coverage
- [ ] Documentation updated
- [ ] Ready for review/merge

---

## Blockers & Questions

### Known Issues
- Issue 1: Description and impact
- Issue 2: Description and impact

### Questions to Resolve
1. Question 1?
2. Question 2?
3. Question 3?

---

## Next Session Prep

**If this session completes successfully:**
- Next focus: [What comes after]
- Need: [Any resources/hardware/info needed]
- Consider: [Things to think about]

**If blocked on [specific thing]:**
- Fallback: [Alternative approach]
- Alternative: [Another path]
- Escalate: [Who/what to consult]

---

## Session Log

**Started:** _[timestamp when work begins]_
**Completed:** _[timestamp when work ends]_
**Outcome:** _[brief summary of what was accomplished]_

### Work Items Completed
- _[fill in as you go]_

### Issues Encountered
- _[track problems for future reference]_

### Follow-up Tasks
- _[anything that needs to be done next time]_

---

## References

- Relevant file 1: `path/to/file`
- Relevant file 2: `path/to/file`
- Documentation: `path/to/docs`
- Related issue/PR: [link if applicable]

---

## Example: Current Session (2025-11-05)

For reference, here's what the current active session looks like:

**Branch:** `session/2025-11-05-integration-testing`
**Focus:** Connect generated VHDL to FSM, validate end-to-end flow

**Primary Goals:**
1. Integrate Generated Register Interface with FSM
   - Wire `basic_probe_driver_custom_inst_shim.vhd` to `fi_probe_interface.vhd`
   - Map register fields to FSM control signals

2. Build CocoTB Test Suite
   - Create basic register read/write tests
   - Test FSM state transitions

3. Python-VHDL Integration Validation
   - Ensure DS1120A driver generates valid register values
   - Test voltage range validation

**Key Files:**
- `bpd/bpd-vhdl/src/fi_probe_interface.vhd` - FSM implementation
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd` - Generated interface
- `bpd/bpd-vhdl/tests/` - CocoTB test directory
- `bpd/bpd-drivers/src/bpd_drivers/ds1120a.py` - Python driver
