# <<09-JUN-2025:18:53>> - Added stable URL signature extractor for Oracle UI

from urllib.parse import urlparse, parse_qs, urlunparse
from utils.logging import debug_log
def get_stable_url_signature(full_url: str) -> str:
	"""
	Extracts a stable base signature from an Oracle Cloud UI URL
	by stripping volatile query parameters.

	Examples of removed params: _afrLoop, _adf.ctrl-state, etc.

	Returns a stable URL identifier that can be used for lookup or comparison.
	"""
	debug_log("Entered");
	try:
		parsed = urlparse(full_url)
		base_path = parsed.path

		# Retain only stable query parameters
		query_params = parse_qs(parsed.query)

		keep_keys = [
			"pageParams",
			"fndGlobalItemNodeId",
			"fndTaskItemNodeId"
		]

		stable_query = {
			k: v for k, v in query_params.items()
			if k in keep_keys
		}

		# Reconstruct the query string
		if stable_query:
			stable_query_str = "&".join(
				f"{key}={value[0]}" for key, value in stable_query.items()
			)
			debug_log(f"Stable query parameters: {stable_query_str}")
			return f"{base_path}?{stable_query_str}"
		else:
			debug_log("No stable query parameters found, returning base path")
			return base_path
	except Exception as e:
		debug_log(f"Error extracting stable URL signature")
		return full_url  # fallback to original if anything fails
