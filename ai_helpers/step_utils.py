def post_login_validation_steps():
	"""
	Return a list of steps to confirm login success and navigate into core pages.
	"""
	return [
		{
			"action": "wait_for_selector",
			"selector": "#menu-tools",
		},
		{
			"action": "click",
			"selector": "#menu-tools"
		},
		{
			"action": "wait_for_timeout",
			"value": "2000"
		},
		{
			"action": "click",
			"selector": "text='Scheduled Processes'"
		}
	]
