#!/bin/bash

# Manual Push Script for Epistemic Engine
# ========================================
# Use this if auto-push requires authentication
#
# USAGE: ./push_manual.sh

set -e

echo ""
echo "======================================"
echo "  EPISTEMIC ENGINE - MANUAL PUSH"
echo "======================================"
echo ""
echo "Repository: https://github.com/NarendraaP/Epistemic-Engine.git"
echo "Branch: main"
echo ""

# Check if we're in correct directory
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo "❌ Error: Not in Epistemic-Engine directory"
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please run this from:"
    echo "  cd /Users/satish/.gemini/antigravity/scratch/Epistemic-Engine"
    echo "  ./push_manual.sh"
    exit 1
fi

# Show current status
echo "Current commit:"
git log --oneline -1
echo ""

# Push with authentication
echo "Pushing to GitHub..."
echo "(You may be prompted for authentication)"
echo ""

if git push -u origin main; then
    echo ""
    echo "======================================"
    echo "✅ CODE IS LIVE ON GITHUB"
    echo "======================================"
    echo ""
    echo "View your repository:"
    echo "  https://github.com/NarendraaP/Epistemic-Engine"
    echo ""
    echo "GitHub Actions will now:"
    echo "  ✓ Run Epistemic Guard tests"
    echo "  ✓ Verify Constitutional compliance"
    echo "  ✓ Generate coverage report"
    echo ""
    echo "Check build status:"
    echo "  https://github.com/NarendraaP/Epistemic-Engine/actions"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ PUSH FAILED"
    echo "======================================"
    echo ""
    echo "Common solutions:"
    echo ""
    echo "1. Authentication Required:"
    echo "   - GitHub may prompt for username/password"
    echo "   - Use Personal Access Token instead of password"
    echo "   - Create token at: https://github.com/settings/tokens"
    echo ""
    echo "2. Use SSH instead of HTTPS:"
    echo "   git remote set-url origin git@github.com:NarendraaP/Epistemic-Engine.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. Use GitHub CLI (gh):"
    echo "   gh auth login"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi
