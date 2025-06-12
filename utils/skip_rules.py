# <<06-JUN-2025:17:13>> - Centralized blacklist logic for skipping nav/action elements
from utils.logging import debug_log

def should_skip_label(label, visited):
	# debug_log(f"🔍 Evaluating label: {label}")
	if not label or label.strip() == "":
		# debug_log("⏭️ Skipped: empty label")
		return True

	if label in visited:
		# debug_log("⏭️ Skipped: already visited")
		return True

	skip_terms = [
		"Skip to main content", "Sign Out", "Settings and Actions", "Favorites",
		"Home", "Navigator", "Logout", "About This Application", "Preferences",
		"Notifications", "Collapse", "Help", "Keyboard Shortcuts","Analytics",
		"Unread Notifications", "Watchlist", "Show More", "Show Less", "Previous", "Next",
    	"Detach", "Sort Ascending", "Sort Descending","Skip to main content","Others",		
	    "Hide Help Icons",	"About This Application",	"Getting Started",	"Reports and Analytics",
	    "Financial Reporting Center",	"Sign Out",	"Google Chrome Help",	"Analytics",	"Product Management",
	    "Cloud Customer Connect",	"Settings and Actions",	"Applications Help",
		"Marketplace", "Home"	, "Getting Started", "Download Desktop",
		
		"Maribel",  "Product Management","Asset"   # custom labels start here
		]  

	if any(term.lower() in label.lower() for term in skip_terms):
		# debug_log(f"⏭️ Skipped: blacklisted by term match → {label}")
		return True

	return False

	return False
