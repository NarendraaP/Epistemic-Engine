# Epistemic Engine - Cloud Deployment Guide

## Auto-Deployment System

### Overview
The Epistemic Engine includes a fully automated deployment system designed for cloud-based editors (Project IDX, Gitpod, Codespaces, etc.).

### Quick Start

```bash
# Make changes to your code
# ...

# Deploy with one command (auto-test, commit, push)
./auto_deploy.sh

# Or with custom commit message
./auto_deploy.sh "Add new feature"
```

### Workflow

The deployment script follows this sequence:

```
1. Run Epistemic Guard (pytest tests/)
   ├─ Pass → Continue
   └─ Fail → ABORT with error message

2. Check for changes
   ├─ No changes → Exit gracefully
   └─ Changes detected → Continue

3. Stage all changes (git add .)

4. Commit with timestamp
   ├─ Custom message provided → Use it
   └─ No message → "Auto-save: YYYY-MM-DD HH:MM:SS"

5. Push to origin/main
   ├─ Remote configured → Push
   └─ No remote → Save locally, show instructions

6. Success! GitHub Actions triggered
```

### First-Time Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Initialize Git (if not already done)
```bash
git init
git branch -M main
```

#### 3. Create GitHub Repository
Go to https://github.com/new and create **"Epistemic-Engine"**

#### 4. Add Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/Epistemic-Engine.git
```

#### 5. First Push
```bash
./auto_deploy.sh "Initial commit: Epistemic Engine v1.0"
```

### Daily Workflow

```bash
# Morning: Start coding
cd Epistemic-Engine

# Make changes...
vim src/ingestion/new_feature.py

# Afternoon: Deploy (auto-tests, commits, pushes)
./auto_deploy.sh

# That's it! ✅
```

### What Happens After Push

GitHub Actions automatically:
1. ✅ Runs test suite across Python 3.7-3.11
2. ✅ Verifies Constitutional compliance
3. ✅ Generates coverage report
4. ✅ Uploads to Codecov
5. ✅ Displays build status

### Error Handling

#### ❌ Tests Failed
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ ABORT: CODE VIOLATED EPISTEMIC STANDARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

One or more tests failed. Fix violations before deploying.
```

**What to do:**
1. Review test output
2. Fix the violation
3. Run tests manually: `pytest tests/ -v`
4. Deploy again: `./auto_deploy.sh`

#### ⚠️ No Remote Configured
```
⚠ No remote configured

To add a remote:
  git remote add origin https://github.com/YOUR_USERNAME/Epistemic-Engine.git

Commit saved locally. Run this script again after adding remote.
```

**What to do:**
1. Create GitHub repository
2. Add remote as shown
3. Run `./auto_deploy.sh` again

### Advanced Usage

#### Custom Commit Messages
```bash
./auto_deploy.sh "Fix: Corrected parallax calculation"
./auto_deploy.sh "Feature: Added binary octree export"
./auto_deploy.sh "Docs: Updated Constitution"
```

#### Skip Auto-Deploy (Manual Control)
```bash
# Run tests only
pytest tests/

# Manual git workflow
git add specific_file.py
git commit -m "Specific message"
git push
```

#### Configure Git User
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### File Structure

```
Epistemic-Engine/
├── auto_deploy.sh          # ← The "One-Click Deploy" button
├── .gitignore              # ← Excludes generated files
├── .github/
│   └── workflows/
│       └── epistemic_guard.yml  # ← GitHub Actions CI/CD
└── tests/                  # ← Tests that must pass before deploy
    ├── test_invariants.py
    ├── test_octree.py
    └── test_schema.py
```

### Troubleshooting

#### Permission Denied
```bash
chmod +x auto_deploy.sh
```

#### pytest Not Found
```bash
pip install pytest pytest-cov
```

#### Push Rejected (Behind Remote)
```bash
git pull origin main --rebase
./auto_deploy.sh
```

#### Merge Conflicts
```bash
git status
# Fix conflicts in marked files
git add .
git rebase --continue
```

### Best Practices

1. **Run tests locally first**
   ```bash
   pytest tests/ -v
   ```

2. **Deploy frequently**
   - Small commits are better than large ones
   - Deploy after each feature/fix

3. **Use descriptive messages**
   ```bash
   ./auto_deploy.sh "Fix: Invariant II validation for negative parallax"
   ```

4. **Check build status**
   - After push, visit: https://github.com/YOUR_USERNAME/Epistemic-Engine/actions
   - Ensure green checkmark ✅

### Cloud Editor Integration

#### Project IDX
```bash
# In terminal
./auto_deploy.sh
```

#### GitHub Codespaces
```bash
# Already has git configured
./auto_deploy.sh
```

#### Gitpod
```bash
# Add to .gitpod.yml for auto-execute
tasks:
  - command: chmod +x auto_deploy.sh
```

### CI/CD Dashboard

Monitor your builds at:
```
https://github.com/YOUR_USERNAME/Epistemic-Engine/actions
```

**Build Badge** (add to README):
```markdown
![Epistemic Guard](https://github.com/YOUR_USERNAME/Epistemic-Engine/actions/workflows/epistemic_guard.yml/badge.svg)
```

---

## Summary

**One command to rule them all:**
```bash
./auto_deploy.sh
```

**What it does:**
1. ✅ Tests your code (Constitutional compliance)
2. ✅ Commits with timestamp
3. ✅ Pushes to GitHub
4. ✅ Triggers CI/CD
5. ❌ Aborts if tests fail

**The Constitution is always enforced!** 🛡️
