import json
from utils.logging import debug_log
from pathlib import Path
from datetime import datetime

class DBWriter:
	def __init__(self, filepath="oracle_ui_dump.jsonl"):
		self.filepath = Path(filepath)

	async def insert_entry(self, data):
		debug_log("Entered")
		data["captured_at"] = datetime.utcnow().isoformat()
		with self.filepath.open("a", encoding="utf-8") as f:
			f.write(json.dumps(data) + "\n")
		debug_log(f"💾 Saved entry: {data['label']}")
		debug_log("Exited")
