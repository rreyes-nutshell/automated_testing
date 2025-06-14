# <<13-JUN-2025:22:40>> - Verifies post-trap state, page stability, icon visibility, and adds initial label

from utils.logging import debug_log
from utils.skip_rules import should_skip_label
from playwright.async_api import Page

async def post_login_nav_ready(page: Page, burgers_visited):
	debug_log("🔁 Running post-login nav prep...")

	try:
		# Confirm we are back on welcome screen before interacting
		current_url = page.url
		debug_log(f"🌐 Current URL before nav prep: {current_url}")
		if "FuseWelcome" not in current_url:
			debug_log("🕓 Waiting for Oracle to redirect to home...")
			await page.wait_for_url("**/FuseWelcome", timeout=6000)

		await page.get_by_role("link", name="Navigator").click()
		debug_log("🍔 Clicked hamburger menu")

		await page.wait_for_timeout(1000)

		show_more = page.get_by_role("link", name="Show More")
		if await show_more.is_visible():
			await show_more.click()
			debug_log("📂 Clicked Show More")
			await page.wait_for_timeout(1000)

		icons = page.locator("a[id^='pt1:_UISnvr']")
		await icons.first.wait_for(state="visible", timeout=4000)

		count = await icons.count()
		debug_log(f"🍔 Burger icon count after reopen: {count}")

		first_label = await icons.nth(0).inner_text()
		first_label = first_label.strip()

		if not should_skip_label(first_label, visited=burgers_visited):
			# burgers_visited.add(first_label)
			debug_log(f"✅ Added initial burger label to visited: {first_label}")

	except Exception as err:
		debug_log(f"❌ Failed post-login nav prep: {err}")

	debug_log("✅ Post-login nav prep complete.")
# 
# <<13-JUN-2025:22:40>> - Verifies hamburger is truly expanded and stable

async def expand_hamburger_menu(page: Page, session_id="unknown"):
	debug_log("Entered")

	try:
		# Check if already expanded based on "Collapse" text visibility
		already_expanded = (
			await page.get_by_text("Collapse Tools").is_visible() or
			await page.get_by_text("Collapse Others").is_visible() or
			await page.get_by_text("Collapse My Enterprise").is_visible()
		)
		if already_expanded:
			debug_log("📂 Menu already expanded, skipping Navigator click.")
			await page.wait_for_timeout(1000)
			debug_log("Exited")
			return True

		# Retry Navigator click
		retries = 3
		for attempt in range(retries):
			try:
				navigator_btn = page.get_by_role("link", name="Navigator")
				await navigator_btn.wait_for(state="visible", timeout=3000)
				await navigator_btn.click()
				await page.wait_for_timeout(1000)
				debug_log("📂 Clicked Navigator")
				break
			except Exception as retry_err:
				debug_log(f"Retry {attempt+1}/{retries} failed: {retry_err}")
				await page.wait_for_timeout(1000)
		else:
			raise TimeoutError("Navigator button never became visible.")

		# Optional Show More
		show_more_link = page.get_by_role("link", name="Show More")
		if await show_more_link.is_visible():
			await show_more_link.click()
			await page.wait_for_timeout(1000)
			debug_log("📂 Clicked Show More")

		# Confirm icons are really visible
		icons = page.locator("a[id^='pt1:_UISnvr']")
		await icons.first.wait_for(state="visible", timeout=5000)
		count = await icons.count()
		debug_log(f"🍔 Confirmed burger icon count: {count}")

	except Exception as e:
		debug_log(f"⚠️ Menu expansion failed: {e}")
		debug_log("Exited")
		return False

	debug_log("Exited")
	return True
