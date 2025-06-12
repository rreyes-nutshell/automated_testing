# <<10-JUN-2025:21:20>> - Utility to detect and dismiss Oracle Cloud modal/popup overlays

import os
from utils.logging import debug_log
# <<10-JUN-2025:21:31>> - Expanded modal/menu overlay handling for Oracle Cloud
# <<10-JUN-2025:21:42>> - Enhanced menu dismissal using JS and forced blur

# <<10-JUN-2025:01:01>> - Added generic Oracle blocking modal detector with escape logic
# <<10-JUN-2025:01:47>> - Handles Oracle modals safely, avoids dismissing legitimate nav, clicks stubborn modals

# <<10-JUN-2025:02:05>> - Refactored modal handler to avoid dismissing legitimate Oracle nav containers and centralize visibility checks
# <<10-JUN-2025:02:32>> - Smart modal handler: tries Escape, falls back to click if still visible
async def dismiss_modal_if_present(page):
	# debug_log("Entered")

	safe_to_ignore = [
		"text='Change Data Access Set'",
		"text='Press escape to exit this popup.'"
	]

	for selector in safe_to_ignore:
		if await page.locator(selector).is_visible():
			debug_log(f"🔐 Ignoring modal '{selector}' to keep burger nav safe")
			return






	try:
		# Target Oracle sticky modals with Escape + fallback click
		text_locator = page.locator("text='Press escape to exit this popup.'").first
		if await text_locator.is_visible():
			debug_log("🛑 Modal detected — attempting Escape")
			await page.keyboard.press("Escape")
			await page.wait_for_timeout(300)

		try:
			cancel_popup = page.locator("text='Change Data Access Set'")
			if await cancel_popup.is_visible():
				debug_log("🧾 Oracle data access popup detected — clicking Cancel")

				cancel_button = page.locator("text='Cancel'").first
				if await cancel_button.is_visible():
					await cancel_button.click()
					await page.wait_for_timeout(500)
					debug_log("✅ Clicked Cancel to dismiss data access popup")
					return
		except Exception as e:
			debug_log(f"⚠️ Failed to dismiss data access popup: {e}")

			# Recheck if still visible after Escape
			if await text_locator.is_visible():
				debug_log("⚠️ Modal still present — attempting click fallback")
				box = await text_locator.bounding_box()
				if not box:
					element = await text_locator.evaluate_handle(
						"""node => {
							let el = node;
							while (el && (!el.offsetWidth || !el.offsetHeight)) {
								el = el.parentElement;
							}
							return el;
						}"""
					)
					box = await element.bounding_box()

				if box:
					click_x = box['x'] + box['width'] / 2
					click_y = box['y'] + box['height'] / 2
					await page.mouse.click(click_x, click_y)
					await page.wait_for_timeout(300)
					debug_log("✅ Clicked modal container after failed Escape")
					return

		# Optionally handle other modal selectors or fallbacks here

	except Exception as e:
		debug_log(f"❌ dismiss_modal_if_present failed: {e}")

	# debug_log("Exited")




# 
# <<10-JUN-2025:21:54>> - Forces a click inside Oracle dropdown menu to dismiss lingering menu overlays

# <<10-JUN-2025:00:45>> - Skip dismissing legit Oracle nav containers like _UISnvr
# <<10-JUN-2025:01:14>> - Skip Oracle nav containers like _UISnvr when dismissing overlays
async def dismiss_oracle_menu_overlay(page):
	debug_log("Entered")
	try:
		menu_candidates = [
			'div[id*="menu"]',
			'div[id*="popup"]',
			'div[id^="ptm:"]',
			'div[id*="pt1"]',
		]

		for selector in menu_candidates:
			# ⛔ Skip Oracle nav menu containers
			if "_UISnvr" in selector or "pt1" in selector:
				debug_log(f"⏭️ Skipping known nav container: {selector}")
				continue

			el = await page.query_selector(selector)
			if el:
				box = await el.bounding_box()
				if box:
					click_x = box['x'] + box['width'] / 2
					click_y = box['y'] + box['height'] / 2
					await page.mouse.click(click_x, click_y)
					await page.wait_for_timeout(300)
					debug_log(f"✅ Clicked center of menu overlay ({selector}) to dismiss")
					break
	except Exception as e:
		debug_log(f"❌ dismiss_oracle_menu_overlay failed: {e}")
	debug_log("Exited")
