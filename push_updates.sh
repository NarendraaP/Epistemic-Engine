#!/bin/bash

# Epistemic Engine - Auto-Push Script
# ====================================
# Convenience script for adding, committing, and pushing changes
#
# USAGE:
#   ./push_updates.sh
#   ./push_updates.sh "Your commit message"

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "======================================"
echo "  Epistemic Engine - Git Push"
echo "======================================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Not a git repository${NC}"
    echo "Run: git init"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    HAS_CHANGES=true
else
    HAS_CHANGES=false
fi

if [ "$HAS_CHANGES" = false ]; then
    echo -e "${YELLOW}⚠ No changes to commit${NC}"
    echo ""
    git status
    exit 0
fi

# Show status
echo -e "${BLUE}Current status:${NC}"
git status --short
echo ""

# Get commit message
if [ -z "$1" ]; then
    echo -e "${BLUE}Enter commit message:${NC}"
    read -r COMMIT_MSG
else
    COMMIT_MSG="$1"
fi

if [ -z "$COMMIT_MSG" ]; then
    echo -e "${RED}✗ Error: Commit message cannot be empty${NC}"
    exit 1
fi

echo ""
echo "======================================"
echo "  Running Pre-Push Checks"
echo "======================================"
echo ""

# Optional: Run tests before pushing
if command -v pytest &> /dev/null; then
    echo -e "${BLUE}Running Epistemic Guard (tests)...${NC}"
    echo ""
    
    if pytest tests/ -v --tb=short; then
        echo ""
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo ""
        echo -e "${RED}✗ Tests failed!${NC}"
        echo ""
        read -p "Push anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Push cancelled."
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ pytest not found, skipping tests${NC}"
    echo "  Install with: pip install pytest"
fi

echo ""
echo "======================================"
echo "  Git Operations"
echo "======================================"
echo ""

# Add all changes
echo -e "${BLUE}Adding changes...${NC}"
git add .
echo -e "${GREEN}✓ Changes added${NC}"
echo ""

# Commit
echo -e "${BLUE}Committing with message:${NC}"
echo "  \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Committed${NC}"
echo ""

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${BLUE}Current branch: ${NC}$CURRENT_BRANCH"
echo ""

# Push
echo -e "${BLUE}Pushing to remote...${NC}"
if git push origin "$CURRENT_BRANCH"; then
    echo ""
    echo "======================================"
    echo -e "${GREEN}✓ Push Successful!${NC}"
    echo "======================================"
    echo ""
    echo "Changes pushed to: $CURRENT_BRANCH"
    echo ""
    echo "GitHub Actions will now:"
    echo "  1. Run Epistemic Guard (test suite)"
    echo "  2. Verify Constitutional compliance"
    echo "  3. Generate coverage report"
    echo ""
    echo "Check build status at:"
    echo "  https://github.com/YOUR_USERNAME/Epistemic-Engine/actions"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Push failed${NC}"
    echo ""
    echo "Common causes:"
    echo "  - No remote configured: git remote add origin <url>"
    echo "  - Branch not tracking remote: git push -u origin $CURRENT_BRANCH"
    echo "  - Authentication required: Check GitHub credentials"
    exit 1
fi
