### <<07-JUN-2025:19:28>> - Expands {placeholders} in test step dict fields using context

def interpolate_step_vars(step: dict, context: dict) -> dict:
	"""
	Replaces placeholders like {login_url}, {username} in step fields using context.
	Mutates and returns the step dict.
	"""
	for key in ["target", "selector", "value"]:
		if key in step and isinstance(step[key], str):
			try:
				step[key] = step[key].format(**context)
			except KeyError as e:
				# Leave unchanged if missing context
				pass
	return step

