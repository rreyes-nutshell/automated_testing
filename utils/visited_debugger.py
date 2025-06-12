# <<11-JUN-2025:13:51>> - Created to support debug output of visited labels

import os
from utils.logging import debug_log

def dump_visited(visited: set):
	debug_log("Entered")
	try:
		dump_path = os.getenv("VISITED_DUMP_FILE", "visited_labels.txt")
		with open(dump_path, "w", encoding="utf-8") as f:
			for label in sorted(visited):
				f.write(label + "\n")
		debug_log(f"📝 Visited labels written to {dump_path}")
	except Exception as e:
		debug_log(f"❌ Failed to dump visited labels: {e}")
	debug_log("Exited")
