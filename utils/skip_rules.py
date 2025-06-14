# <<13-JUN-2025:22:20>> - Merged DataTab skip logic into central blacklist filter
from utils.logging import debug_log

def should_skip_label(label, visited):
	# debug_log(f"🔍 Evaluating label: {label}")
	if not label or label.strip() == "":
		# debug_log("⏭️ Skipped: empty label")
		return True

	label = label.strip()
	lower = label.lower()

	if label in visited:
		# debug_log("⏭️ Skipped: already visited")
		return True

	# Custom junk skip logic (formerly lost)
	if len(label) < 4:
		debug_log(f"⏭️ Skipped: label too short → {label}")
		return True

	skip_values = {
		"yes", "no", "edit", "actions", "processed", "pending", "invoice", "close",
		"cancel", "done", "save", "reject", "1", "2", "3", "4", "5"
	}
	if lower in skip_values:
		return True

	if label.replace(",", "").replace(".", "").isdigit():
		return True

	if any(x in lower for x in ["date", "amount", "currency"]):
		return True

	# Existing skip terms
	skip_terms = [
		"Skip to main content", "Sign Out", "Settings and Actions", "Favorites",
		"Home", "Navigator", "Logout", "About This Application", "Preferences",
		"Notifications", "Collapse", "Help", "Keyboard Shortcuts","Analytics",
		"Unread Notifications", "Watchlist", "Show More", "Show Less", "Previous", "Next",
		"Detach", "Sort Ascending", "Sort Descending","Skip to main content","Others",		
		"Hide Help Icons",	"About This Application",	"Getting Started",	"Reports and Analytics",
		"Financial Reporting Center",	"Sign Out",	"Google Chrome Help",	"Analytics",	"Product Management",
		"Cloud Customer Connect",	"Settings and Actions",	"Applications Help",
		"Marketplace", "Home"	, "Getting Started", "Download Desktop","Format",	"View",
		"Download Desktop Integration Installer", "File Import and Export","Setup and Maintenance",
		"Import Management", "Export Management", "Collaboration Messaging", "Feature Updates",
		"Getting Started", "Financial Reporting Center", "New Features","Offerings","PO Inquiry",
		"Maribel",  "Product Management","Asset"
	]

	if any(term.lower() in lower for term in skip_terms):
		# debug_log(f"⏭️ Skipped: blacklisted by term match → {label}")
		return True

	return False
