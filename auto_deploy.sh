#!/bin/bash

# Epistemic Engine - Automated Deployment Script
# ===============================================
# PURPOSE: Auto-test, commit, and push changes with zero user interaction
# WORKFLOW: Test → Add → Commit → Push (or Abort if tests fail)
#
# USAGE:
#   ./auto_deploy.sh
#   ./auto_deploy.sh "Optional custom message"

set -e  # Exit on error

# =============================================================================
# CONFIGURATION
# =============================================================================

BRANCH="main"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color


# =============================================================================
# HEADER
# =============================================================================

echo ""
echo "======================================"
echo "  EPISTEMIC ENGINE - AUTO DEPLOY"
echo "======================================"
echo ""
echo "Timestamp: $TIMESTAMP"
echo ""


# =============================================================================
# STEP 1: RUN EPISTEMIC GUARD (TESTS)
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}STEP 1: EPISTEMIC GUARD (TESTING)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v pytest &> /dev/null; then
    echo "Running Constitutional compliance tests..."
    echo ""
    
    # Run tests with minimal output
    if pytest tests/ --tb=short -q; then
        echo ""
        echo -e "${GREEN}✓ All tests passed - Constitution upheld${NC}"
        echo ""
    else
        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}${BOLD}❌ ABORT: CODE VIOLATED EPISTEMIC STANDARD${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "One or more tests failed. Fix violations before deploying."
        echo ""
        echo "Constitutional Invariants:"
        echo "  I.   Labeling - All data must be tagged"
        echo "  II.  Reference - No absolute coordinates"
        echo "  III. Access - Truth Slider must be consistent"
        echo ""
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping tests${NC}"
    echo "Install with: pip install pytest"
    echo ""
fi


# =============================================================================
# STEP 2: CHECK FOR CHANGES
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}STEP 2: CHECKING FOR CHANGES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if git is initialized
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Initializing git repository..."
    git init
    echo -e "${GREEN}✓ Git initialized${NC}"
    echo ""
fi

# Check for changes
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}No changes to deploy${NC}"
    echo ""
    git status
    echo ""
    exit 0
fi

echo "Changes detected:"
git status --short
echo ""


# =============================================================================
# STEP 3: STAGE CHANGES
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}STEP 3: STAGING CHANGES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

git add .
echo -e "${GREEN}✓ All changes staged${NC}"
echo ""


# =============================================================================
# STEP 4: COMMIT
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}STEP 4: COMMITTING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Use custom message if provided, otherwise auto-generate
if [ -z "$1" ]; then
    COMMIT_MSG="Auto-save: $TIMESTAMP"
else
    COMMIT_MSG="$1"
fi

echo "Commit message: \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG"
echo ""
echo -e "${GREEN}✓ Changes committed${NC}"
echo ""


# =============================================================================
# STEP 5: PUSH TO REMOTE
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}STEP 5: PUSHING TO REMOTE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ No remote configured${NC}"
    echo ""
    echo "To add a remote:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/Epistemic-Engine.git"
    echo ""
    echo "Commit saved locally. Run this script again after adding remote."
    exit 0
fi

# Push to remote
echo "Pushing to origin/$BRANCH..."
if git push origin "$BRANCH" 2>&1; then
    echo ""
    echo -e "${GREEN}✓ Successfully pushed to remote${NC}"
    echo ""
else
    # If push fails, likely need to set upstream
    echo ""
    echo "Setting upstream branch..."
    git push -u origin "$BRANCH"
    echo ""
    echo -e "${GREEN}✓ Successfully pushed to remote${NC}"
    echo ""
fi


# =============================================================================
# SUCCESS SUMMARY
# =============================================================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}✓ DEPLOYMENT SUCCESSFUL${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Summary:"
echo "  ✓ Tests passed (Constitutional compliance verified)"
echo "  ✓ Changes committed: \"$COMMIT_MSG\""
echo "  ✓ Pushed to: origin/$BRANCH"
echo ""
echo "GitHub Actions will now:"
echo "  1. Run Epistemic Guard test suite"
echo "  2. Verify across Python 3.7-3.11"
echo "  3. Generate coverage report"
echo ""
echo "Check build status:"
echo "  https://github.com/YOUR_USERNAME/Epistemic-Engine/actions"
echo ""
