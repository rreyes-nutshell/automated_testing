# <<13-JUN-2025:20:59>> - Forces icon DOM refresh and visible check before traversal

from utils.logging import debug_log
from utils.selector_resolver import get_selector
from utils.modal_handler import dismiss_modal_if_present
from utils.skip_rules import should_skip_label
from utils.nav_helpers import expand_hamburger_menu  # <<13-JUN-2025:21:12>> - Added to ensure menu is open between crawls

# <<13-JUN-2025:22:02>> - Adds index-based resume to avoid burger loop trap

async def launch_next_unclicked_icon(page, burgers_visited, start_index=0):
	debug_log(f"Entered launch_next_unclicked_icon (starting from index {start_index})")

	try:
		await dismiss_modal_if_present(page=page)
		await page.wait_for_timeout(500)

		# <<13-JUN-2025:21:12>> - Ensure menu is open before accessing icons
		await expand_hamburger_menu(page)

		icons = page.locator("a[id^='pt1:_UISnvr']")
		await icons.first.wait_for(state="visible", timeout=3000)

		total = await icons.count()
		if total == 0:
			debug_log("⚠️ No hamburger icons detected after menu open.")
			debug_log("Exited launch_next_unclicked_icon — no icon launched")
			return None, start_index

		debug_log(f"🍔 Found {total} top-level hamburger icons")
		debug_log(f"🍔 burgers_visited so far: {sorted(list(burgers_visited))}")

		for i in range(start_index, total):
			element = icons.nth(i)
			label = None

			try:
				if not await element.is_visible():
					continue
				label = await element.inner_text()
				label = label.strip()
			except Exception as label_err:
				debug_log(f"⚠️ Skipping element [{i}] due to error: {label_err}")
				continue

			if not label or label in burgers_visited:
				continue

			if should_skip_label(label, visited=burgers_visited):
				debug_log(f"⏭️ Skipping icon per rules: {label}")
				continue

			debug_log(f"▶️ Launching icon: {label}")
			await element.scroll_into_view_if_needed()

			try:
				prev_heading = None
				h_el = await page.query_selector("h1, h2")
				if h_el:
					prev_heading = await h_el.inner_text()

				await element.click(timeout=5000, force=True)
				await page.wait_for_timeout(1500)

				new_heading = None
				h2 = await page.query_selector("h1, h2")
				if h2:
					new_heading = await h2.inner_text()

				debug_log(f"🧭 Previous heading: {prev_heading}")
				debug_log(f"🧭 New heading: {new_heading}")

				if prev_heading and new_heading == prev_heading:
					debug_log(f"❗ Heading did not change after clicking '{label}' — skipping crawl.")
					continue

				# ✅ Only add to visited after successful heading change
				burgers_visited.add(label)
				debug_log(f"📋 burgers_visited now: {sorted(list(burgers_visited))}")
				debug_log("Exited launch_next_unclicked_icon")
				return label, i + 1

			except Exception as click_err:
				debug_log(f"❌ Click failed for [{label}]: {click_err}")
				continue

	except Exception as launch_err:
		debug_log(f"❌ Failed in launch_next_unclicked_icon: {launch_err}")

	debug_log("Exited launch_next_unclicked_icon — no icon launched")
	return None, start_index
