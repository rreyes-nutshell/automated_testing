if __name__ == "__main__":
	import asyncio
	import os

	async def main():
		selector = "a#pt1\\:_UISnvr\\:0\\:nv_itemNode_procurement_suppliers"
		login_url = "https://your.oraclecloud.com"  # use your real URL
		username = "your_username"
		password = os.getenv("ORA_PW")  # or hardcode for test

		html = await run_single_selector_step(selector, login_url, username, password)
		print("✅ Finished. HTML length:", len(html) if html else "None")

	asyncio.run(main())