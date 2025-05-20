#!/bin/bash

# Ensure you're in a Git repo
if [ ! -d .git ]; then
	echo "❌ Not a Git repository. Run this inside your Git project folder."
	exit 1
fi

# Stage all changes (new, modified, deleted)
git add -A

# Commit with a message
git commit -m "🚀 WIP: Updated login flow, step filtering, and Playwright script runner"

# Optional: push to origin/main (uncomment if needed)
# git push origin main

