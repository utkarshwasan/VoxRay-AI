## File 2: GETTING_STARTED.md

````markdown
# VoxRay AI v2.0 - Getting Started Guide

**Read this FIRST before allocating any agents**

---

## 🎬 Quick Start (5 Minutes)

### Prerequisites

- [ ] You have the VoxRay AI codebase cloned
- [ ] You have Google Antigravity IDE access
- [ ] You understand the current system (React 18 + FastAPI + Stack Auth)
- [ ] You've reviewed Eval #2 requirements

### Step-by-Step Setup

#### 1. Copy Implementation Files

```bash
# Navigate to your VoxRay AI project root
cd /path/to/voxray-ai

# Create Implementation_v2 directory
mkdir -p Implementation_v2/{AGENTS,SHARED}

# Copy all files from this package
cp -r [download-location]/Implementation_v2/* Implementation_v2/

# Create shared context directory
mkdir -p shared_context
2. Initialize Shared Context
Bash

# Copy template to working file
cp Implementation_v2/SHARED/00_CTX_SYNC_TEMPLATE.md shared_context/CTX_SYNC.md

# Verify
ls -la shared_context/
# Should show: CTX_SYNC.md
3. Review Critical Files
MUST READ (15 minutes):

SHARED/01_MUST_PRESERVE.md - What NOT to break ⚠️
SHARED/04_TIMELINE.md - 24-day schedule
MASTER_PLAN.md - This overview
GOOD TO READ (10 minutes):

SHARED/02_QUALITY_GATES.md - Success criteria
SHARED/03_API_CONTRACTS.md - Interface definitions
4. Start with AG-00 (Migration Lead)
Bash

# Open the first agent instructions
cat Implementation_v2/AGENTS/AG-00_MigrationLead.md

# In Antigravity, allocate yourself or a team member as AG-00
# Follow the instructions in that file
🧭 Navigation Guide
Understanding File Structure
text

Implementation_v2/
├── MASTER_PLAN.md              # ← Start here for overview
├── GETTING_STARTED.md          # ← You are here
│
├── AGENTS/                     # Individual agent instructions
│   ├── AG-00_MigrationLead.md     # Phase 0 (Days 1-2)
│   ├── AG-01_ModelArchitect.md    # Phase 1 (Days 3-7)
│   ├── AG-02_PipelineEngineer.md  # Phase 1b (Days 5-9)
│   ├── AG-03_ClinicalIntegrator.md # Phase 2 (Days 7-13)
│   ├── AG-04_VoiceSpecialist.md   # Phase 3 (Days 10-16)
│   ├── AG-05_DevOpsArchitect.md   # Phase 4 (Days 13-19)
│   ├── AG-06_FullStackDeveloper.md # Phase 6 (Days 7-21)
│   ├── AG-07_DataScientist.md     # Phase 5 (Days 15-20)
│   ├── AG-08_QualityAssurance.md  # Phases 1-7 (Days 3-21)
│   └── AG-09_DocumentationLead.md # Phase 7 (Days 18-22)
│
└── SHARED/                     # Common reference files
    ├── 00_CTX_SYNC_TEMPLATE.md    # Coordination template
    ├── 01_MUST_PRESERVE.md        # What NOT to break
    ├── 02_QUALITY_GATES.md        # Success criteria
    ├── 03_API_CONTRACTS.md        # Interface specs
    ├── 04_TIMELINE.md             # 24-day schedule
    ├── 05_COST_ESTIMATION.md      # Budget planning
    ├── 06_FEATURE_FLAGS.md        # Feature flag guide
    └── 07_TROUBLESHOOTING.md      # Common issues
How Agent Files Work
Each AG-XX_AgentName.md file contains:

Role Definition - What this agent does
Dependencies - Which agents must complete first
Required Reading - Which SHARED files to read
Tasks - Step-by-step implementation
Code - Complete implementation code
Self-Checks - How to verify your work
Handoff - What to pass to next agent
🔄 Workflow for Each Agent
When you start working as an agent:

1. Read Phase
Bash

# Open your agent file
cat Implementation_v2/AGENTS/AG-0X_YourRole.md

# Read required SHARED files (listed at top)
cat Implementation_v2/SHARED/01_MUST_PRESERVE.md
cat Implementation_v2/SHARED/02_QUALITY_GATES.md
# etc.

# Check CTX_SYNC for blockers
cat shared_context/CTX_SYNC.md
2. Execute Phase
Bash

# Create your status file
cat > shared_context/AG-0X_status.json << 'EOF'
{
  "agent": "AG-0X",
  "status": "In Progress",
  "current_task": "Task 1",
  "progress": 0,
  "blockers": []
}
EOF

# Work through tasks sequentially
# Update status after each task
3. Update Phase
Bash

# After each task, update CTX_SYNC.md
# Find your row in the Agent Status Board
# Change status: ⏳ → 🔄 → ✅

# Update progress percentage
# Note any blockers
4. Verify Phase
Bash

# Run self-checks (commands in your agent file)
pytest tests/...
python scripts/verify_...

# Run quality gate check
python scripts/check_quality_gate.py --phase X
5. Handoff Phase
Bash

# Mark complete in CTX_SYNC.md
# Create handoff notes
cat > shared_context/AG-0X_handoff.md << 'EOF'
# AG-0X Handoff Notes

## Completed
- Task 1: ✅
- Task 2: ✅

## Outputs
- File X created at path/to/file
- Model Y saved at path/to/model

## Next Steps for Dependent Agents
- AG-0Y should use output from path/to/file
- AG-0Z can now start Task 3

## Known Issues
- None

## Recommendations
- Consider optimizing X in future iteration
EOF

# Notify next agent (update CTX_SYNC)
📞 Communication Channels
Between Agents
Primary: shared_context/CTX_SYNC.md

Update your status here
Check other agents' progress
Note blockers and dependencies
Secondary: Individual status files

shared_context/AG-0X_status.json for machine-readable status
shared_context/AG-0X_handoff.md for human notes
To Human Coordinator
Blockers: Update CTX_SYNC.md with blocker tag ⚠️

Questions: Add to "Questions Queue" section in CTX_SYNC.md

Urgent: Flag in CTX_SYNC.md with 🚨

⚠️ Common Mistakes to Avoid
❌ Don't Do This
Skipping MUST_PRESERVE.md

Result: Breaking production system
Fix: Read it FIRST, always
Not updating CTX_SYNC.md

Result: Other agents blocked
Fix: Update after EVERY task
Starting before dependencies complete

Result: Wasted work, conflicts
Fix: Check CTX_SYNC.md first
Not running quality checks

Result: Fails at quality gate
Fix: Run checks after each task
Modifying other agents' files

Result: Merge conflicts, chaos
Fix: Only modify your outputs
✅ Do This Instead
Read all required SHARED files
Check CTX_SYNC.md for dependencies
Execute tasks sequentially
Update CTX_SYNC.md frequently
Run self-checks often
Communicate blockers immediately
🎯 Success Indicators
You're on track if:

✅ CTX_SYNC.md is updated daily
✅ No agent starts before dependencies complete
✅ Quality checks pass after each task
✅ No modifications to MUST_PRESERVE items
✅ All agents communicate via CTX_SYNC.md
You're off track if:

❌ Multiple agents working without coordination
❌ Backward compatibility tests failing
❌ CTX_SYNC.md not updated in 24 hours
❌ Quality gates bypassed
❌ MUST_PRESERVE items modified
📚 Additional Resources
Timeline Details: SHARED/04_TIMELINE.md
Quality Criteria: SHARED/02_QUALITY_GATES.md
Troubleshooting: SHARED/07_TROUBLESHOOTING.md
Cost Planning: SHARED/05_COST_ESTIMATION.md
🚀 Ready to Start?
✅ Files copied to Implementation_v2/
✅ shared_context/CTX_SYNC.md initialized
✅ Read SHARED/01_MUST_PRESERVE.md
✅ Understand the workflow
Next Step:

Bash

# Start with AG-00
cat Implementation_v2/AGENTS/AG-00_MigrationLead.md
Let's build VoxRay AI v2.0! 🎉
```
````
