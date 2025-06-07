#!/bin/bash
echo "📦 Checking Docker Build Context: $(pwd)"
echo "---------------------------------------"

# 1. Show total build context size
echo -e "\n🧮 Total context size (du -sh):"
du -sh .

# 2. Top 15 largest folders/files
echo -e "\n📏 Top 15 largest items in context:"
du -ah . | sort -rh | head -n 15

# 3. List ignored files (if .dockerignore exists and Docker is installed)
if [ -f .dockerignore ]; then
	echo -e "\n🚫 Checking what .dockerignore is excluding..."
	tar -cf - . | docker run --rm -i alpine tar -tvf - > /tmp/context_files.txt

	echo -e "\n📋 Sample of files actually being sent to Docker:"
	head -n 15 /tmp/context_files.txt

	echo -e "\n🔍 Check if 'logs/', '.venv/', and '*.html' are excluded."
else
	echo "⚠️  .dockerignore not found — everything is going into the image!"
fi

