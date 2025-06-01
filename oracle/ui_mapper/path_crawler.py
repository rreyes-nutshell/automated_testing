# --- ORIGINAL CONTENT COMMENTED OUT ---
# from utils.logging import debug_log
# from utils.db_utils import get_db_connection
# from oracle.login_steps import run_oracle_login_steps
# from oracle.ui_mapper import extractor
# from oracle.ui_mapper.db_writer import DBWriter
# from datetime import datetime
# from dotenv import load_dotenv
# import os
#
# async def crawl_path_from_selector(page, label, username, password, login_url, crawler_name, session_id, already_logged_in=False):
# 	debug_log("Entered")
# 	load_dotenv(verbose=True)
# 	writer = DBWriter("oracle_ui_dump.jsonl")
#
# 	if not already_logged_in:
# 		await run_oracle_login_steps(page, login_url, username, password)
# 		debug_log("🔐 Oracle login completed inside crawler")
#
# 	try:
# 		debug_log(f"🔍 Navigating to selector: {label}")
# 		await page.wait_for_selector(label, timeout=15000)
# 		element = page.locator(label)
# 		label_before_click = await element.inner_text()
# 		aria_label = await element.get_attribute("aria-label")
# 		title_attr = await element.get_attribute("title")
# 		debug_log(f"🔍 Found element: {label_before_click} (aria-label: {aria_label}, title: {title_attr})")
#
# 		try:
# 			debug_log("🔄 Attempting to click element")
# 			async with page.expect_navigation(wait_until="load", timeout=10000):
# 				debug_log("🔄 Waiting for navigation")
# 				await element.click()
# 				debug_log("🔄 Navigation completed")
# 		except Exception as nav_err:
# 			debug_log(f"⚠️ Navigation didn't happen: {nav_err}")
# 			await element.click()  # fallback click
#
# 		print("📍 Current URL:", page.url)
#
# 		extracted = {
# 			"label": label_before_click,
# 			"selector": label,
# 			"url": page.url,
# 			"category": "TBD",
# 			"page_id": None,
# 			"aria_label": aria_label,
# 			"title_attr": title_attr
# 		}
# 		debug_log(f"📍 Extracted metadata: {extracted}")
#
# 		if extracted:
# 			await writer.insert_entry({**extracted, "crawler_name": crawler_name, "session_id": session_id})
#
# 			with get_db_connection() as conn:
# 				debug_log("Inserting into DB")
# 				cur = conn.cursor()
# 				cur.execute(
# 					"""
# 					INSERT INTO ui_pages (
# 						page_name, selector, url, category, captured_at, page_id,
# 						crawler_name, session_id,
# 						is_external, has_real_url, aria_label, title_attr
# 					) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
# 					""",
# 					(
# 						extracted["label"],
# 						extracted["selector"],
# 						extracted["url"],
# 						extracted["category"],
# 						datetime.utcnow(),
# 						extracted.get("page_id"),
# 						crawler_name,
# 						session_id,
# 						extracted.get("aria_label"),
# 						extracted.get("title_attr"),
# 					)
# 				)
# 				conn.commit()
#
# 		# Trigger full nav extraction
# 		path_id = extractor.insert_ui_path(session_id, path_name=extracted["label"] or "Unknown")
# 		await extractor.extract_page_contents(page, session_id, path_id)
#
# 	except Exception as e:
# 		debug_log(f"⚠️ Error navigating to selector: {e}")
#
# 	debug_log("Exited")


# --- UPDATED VERSION BELOW ---
# from utils.logging import debug_log
# from utils.db_utils import get_db_connection
# from oracle.login_steps import run_oracle_login_steps
# from oracle.ui_mapper import extractor
# from oracle.ui_mapper.db_writer import DBWriter
# from datetime import datetime
# from dotenv import load_dotenv
# import os


# async def crawl_path_from_selector(
# 	page,
# 	label,
# 	username,
# 	password,
# 	login_url,
# 	crawler_name,
# 	session_id,
# 	already_logged_in=False,
# 	selector=None
# ):
# 	debug_log("Entered")
# 	load_dotenv(verbose=True)
# 	writer = DBWriter("oracle_ui_dump.jsonl")

# 	if not already_logged_in:
# 		debug_log("🔐 Logging in with Oracle credentials")
# 		debug_log(f"🔐 Username: {username}")
# 		debug_log(f"🔐 Login URL: {login_url}")
# 		await run_oracle_login_steps(page, login_url, username, password)
# 		debug_log("🔐 Oracle login completed inside crawler")
# 	else:
# 		debug_log("🔐 Skipping login; already authenticated")

# 	try:
# 		active_selector = selector or label
# 		debug_log(f"🔍 Final selector being used for navigation: {active_selector}")
# 		await page.wait_for_selector(active_selector, timeout=15000)
# 		element = page.locator(active_selector)
# 		label_before_click = await element.inner_text()
# 		aria_label = await element.get_attribute("aria-label")
# 		title_attr = await element.get_attribute("title")
# 		debug_log(f"🔍 Found element: {label_before_click} (aria-label: {aria_label}, title: {title_attr})")

# 		try:
# 			debug_log("🔄 Attempting to click element")
# 			async with page.expect_navigation(wait_until="load", timeout=10000):
# 				debug_log("🔄 Waiting for navigation")
# 				await element.click()
# 				debug_log("🔄 Navigation completed")
# 		except Exception as nav_err:
# 			debug_log(f"⚠️ Navigation didn't happen: {nav_err}")
# 			await element.click()  # fallback click

# 		print("📍 Current URL:", page.url)

# 		extracted = {
# 			"label": label_before_click,
# 			"selector": active_selector,
# 			"url": page.url,
# 			"category": "TBD",
# 			"page_id": None,
# 			"aria_label": aria_label,
# 			"title_attr": title_attr
# 		}
# 		debug_log(f"📍 Extracted metadata: {extracted}")

# 		if extracted:
# 			await writer.insert_entry({**extracted, "crawler_name": crawler_name, "session_id": session_id})

# 			with get_db_connection() as conn:
# 				debug_log("Inserting into DB")
# 				cur = conn.cursor()
# 				cur.execute(
# 					"""
# 					INSERT INTO ui_pages (
# 						page_name, selector, url, category, captured_at, page_id,
# 						crawler_name, session_id,
# 						is_external, has_real_url, aria_label, title_attr
# 					) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
# 					""",
# 					(
# 						extracted["label"],
# 						extracted["selector"],
# 						extracted["url"],
# 						extracted["category"],
# 						datetime.utcnow(),
# 						extracted.get("page_id"),
# 						crawler_name,
# 						session_id,
# 						extracted.get("aria_label"),
# 						extracted.get("title_attr"),
# 					)
# 				)
# 				conn.commit()

# 		# Trigger full nav extraction
# 		path_id = extractor.insert_ui_path(session_id, path_name=extracted["label"] or "Unknown")
# 		await extractor.extract_page_contents(page, session_id, path_id)

# 	except Exception as e:
# 		debug_log(f"⚠️ Error navigating to selector: {e}")

# 	debug_log("Exited")

## 5/30 version that worked prior to cookies 

# from utils.logging import debug_log
# from utils.db_utils import get_db_connection
# from oracle.login_steps import run_oracle_login_steps
# from oracle.ui_mapper import extractor
# from oracle.ui_mapper.db_writer import DBWriter
# from services.playwright_runner import run_browser_script  # ✅ central import
# from datetime import datetime
# from dotenv import load_dotenv
# import os


# async def crawl_path_from_selector(
# 	page,
# 	label,
# 	username,
# 	password,
# 	login_url,
# 	crawler_name,
# 	session_id,
# 	already_logged_in=False,
# 	selector=None,
# 	browser=None
# ):
# 	debug_log("Entered")
# 	load_dotenv(verbose=True)
# 	writer = DBWriter("oracle_ui_dump.jsonl")

# 	debug_log(f"username: {username}")
# 	debug_log(f"login_url: {login_url}")
# 	if not already_logged_in:
# 		debug_log("🔐 Logging in with Oracle credentials")
# 		await run_oracle_login_steps(page, login_url, username, password)
# 		debug_log("🔐 Oracle login completed inside crawler"	)
	
# 	debug_log(f"🔍 Navigating to selector: {label}")
# 	debug_log(f"🔍 Final selector being used for navigation: {selector or label}")
# 	debug_log(f"session_id: {session_id}")
# 	# ✅ Use provided selector or fallback to labe
	

# 	# ✅ Build the same step sequence as the Run button
# 	steps = [
# 		{"action": "wait_for_selector", "selector": selector},
# 		{"action": "click", "selector": selector},
# 		{"action": "screenshot", "value": None},
# 		{"action": "log_result", "value": None},
# 	]


	
# 	try:
# 		# ✅ Execute navigation using shared runner for consistency
# 		await run_browser_script(
# 			steps=steps,
# 			session_id=session_id,
# 			login_url=login_url,
# 			username=username,
# 			password=password
# 			# page=page,
# 			# browser=browser,
# 			# already_logged_in=already_logged_in
# 		)

# 		# ✅ After navigation, extract metadata
# 		url = page.url
# 		element = page.locator(selector)
# 		label_before_click = await element.inner_text()
# 		aria_label = await element.get_attribute("aria-label")
# 		title_attr = await element.get_attribute("title")

# 		extracted = {
# 			"label": label_before_click,
# 			"selector": selector,
# 			"url": url,
# 			"category": "TBD",
# 			"page_id": None,
# 			"aria_label": aria_label,
# 			"title_attr": title_attr
# 		}
# 		debug_log(f"📍 Extracted metadata: {extracted}")

# 		if extracted:
# 			await writer.insert_entry({**extracted, "crawler_name": crawler_name, "session_id": session_id})

# 			with get_db_connection() as conn:
# 				debug_log("Inserting into DB")
# 				cur = conn.cursor()
# 				cur.execute(
# 					"""
# 					INSERT INTO ui_pages (
# 						page_name, selector, url, category, captured_at, page_id,
# 						crawler_name, session_id,
# 						is_external, has_real_url, aria_label, title_attr
# 					) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, %s, %s)
# 					""",
# 					(
# 						extracted["label"],
# 						extracted["selector"],
# 						extracted["url"],
# 						extracted["category"],
# 						datetime.utcnow(),
# 						extracted.get("page_id"),
# 						crawler_name,
# 						session_id,
# 						extracted.get("aria_label"),
# 						extracted.get("title_attr"),
# 					)
# 				)
# 				conn.commit()

# 		# ✅ Trigger full nav extraction
# 		path_id = extractor.insert_ui_path(session_id, path_name=extracted["label"] or "Unknown")
# 		await extractor.extract_page_contents(page, session_id, path_id)

# 	except Exception as e:
# 		debug_log(f"⚠️ Error navigating to selector: {e}")

# 	debug_log("Exited")
#
# 5/31 version
#
# <<31-MAY-2025:16:28>> - Merged cookie-based persistence and DOM extraction into existing path_crawler version
# <<31-MAY-2025:16:50>> - Merged run_browser_script reuse of page/browser and login flag into path_crawler
# from utils.logging import debug_log
# from utils.db_utils import get_db_connection
# from oracle.login_steps import run_oracle_login_steps
# from oracle.ui_mapper import extractor
# from oracle.ui_mapper.db_writer import DBWriter
# # services.playwright_runner.run_browser_script now accepts page, browser, already_logged_in
# from services.playwright_runner import run_browser_script  # ✅ central import
# from datetime import datetime
# from dotenv import load_dotenv
# from utils.selectors import ensure_escaped_selector
# import os


# # <<31-MAY-2025:18:30>> – Adjusted unpack of run_browser_script return value
# # <<31-MAY-2025:20:50>> – Added ensure_escaped_selector import and escaped selector in locator calls

# # … other imports above remain unchanged …

# async def crawl_path_from_selector(
# 	page,
# 	label,
# 	username,
# 	password,
# 	login_url,
# 	crawler_name,
# 	session_id,
# 	already_logged_in=False,
# 	selector=None,
# 	browser=None
# ):
# 	"""
# 	<<31-MAY-2025:16:50>> – Execute navigation, ensure single login via cookie,
# 	then insert parent and child DOM. Modified to reuse existing page/browser via run_browser_script.
# 	"""
# 	debug_log("Entered crawl_path_from_selector")
# 	load_dotenv(verbose=True)
# 	writer = DBWriter("oracle_ui_dump.jsonl")

# 	debug_log(f"username: {username}")
# 	debug_log(f"login_url: {login_url}")
# 	debug_log(f"session_id: {session_id}")

# 	if selector:
# 		debug_log(f"🔍 Navigating to selector: {label}")
# 		debug_log(f"🔍 Final selector being used for navigation: {selector}")

# 		# ✅ Build the same step sequence as the Run button
# 		steps = [
# 			{"action": "wait_for_selector", "selector": selector},
# 			{"action": "click", "selector": selector},
# 			{"action": "screenshot", "value": None},
# 			{"action": "log_result", "value": None},
# 		]

# 		try:
# 			# <<31-MAY-2025:18:30>> – Modify unpack to match run_browser_script’s new signature
# 			# page, browser, already_logged_in = await run_browser_script(
# 			#	steps=steps,
# 			#	session_id=session_id,
# 			#	login_url=login_url,
# 			#	username=username,
# 			#	password=password,
# 			#	page=page,                   # ▶️ reuse existing page
# 			#	browser=browser,             # ▶️ reuse existing browser context
# 			#	already_logged_in=already_logged_in  # ▶️ skip login if done
# 			# )
# 			new_page, new_browser, new_flag = await run_browser_script(
# 				steps=steps,
# 				session_id=session_id,
# 				login_url=login_url,
# 				username=username,
# 				password=password,
# 				page=page,                   # ▶️ reuse existing page
# 				browser=browser,             # ▶️ reuse existing browser context
# 				already_logged_in=already_logged_in  # ▶️ skip login if done
# 			)
# 			# <<31-MAY-2025:18:30>> – Update locals to whichever object non-None was returned
# 			page = new_page or page
# 			browser = new_browser or browser
# 			already_logged_in = new_flag

# 			# ✅ After navigation, extract metadata
# 			url = page.url

# 			# <<31-MAY-2025:20:50>> – Escape selector before using in locator
# 			escaped_selector = ensure_escaped_selector(selector)
# 			debug_log(f"🔁 Ensured selector in crawler: {escaped_selector}")
# 			element = page.locator(escaped_selector)
# 			label_before_click = await element.inner_text()
# 			aria_label = await element.get_attribute("aria-label")
# 			title_attr = await element.get_attribute("title")

# 			extracted = {
# 				"label": label_before_click,
# 				"selector": escaped_selector,
# 				"url": url,
# 				"category": "TBD",
# 				"page_id": None,
# 				"aria_label": aria_label,
# 				"title_attr": title_attr
# 			}

# 			# Insert parent row into ui_paths (or whichever table)
# 			conn = get_db_connection()
# 			cur = conn.cursor()
# 			cur.execute(
# 				"""
# 				INSERT INTO ui_paths(session_id, path_name, url, category, aria_label, title_attr, creation_date, created_by)
# 				VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
# 				""",
# 				(
# 					session_id,
# 					extracted["label"],
# 					extracted["url"],
# 					extracted["category"],
# 					extracted["aria_label"],
# 					extracted["title_attr"],
# 					os.getenv("CURRENT_USER", "system")
# 				)
# 			)
# 			conn.commit()

# 			# ✅ Trigger full nav extraction under this parent
# 			path_id = extractor.insert_ui_path(session_id, path_name=extracted["label"] or "Unknown")
# 			await extractor.extract_page_contents(page, session_id, path_id)

# 		except Exception as e:
# 			debug_log(f"⚠️ Error navigating to selector: {e}")

# 	debug_log("Exited crawl_path_from_selector")
# 	# ▶️ Return page, browser, and login flag so caller can maintain session
# 	return page, browser, already_logged_in
#
# 5/31 version above.  clicks into multipe oracle pages, extracts metadata
#
from utils.logging import debug_log
from utils.db_utils import get_db_connection
from oracle.login_steps import run_oracle_login_steps
from oracle.ui_mapper import extractor
from oracle.ui_mapper.db_writer import DBWriter
# services.playwright_runner.run_browser_script now accepts page, browser, already_logged_in
from services.playwright_runner import run_browser_script  # ✅ central import
from datetime import datetime
from dotenv import load_dotenv
from utils.selectors import ensure_escaped_selector
import os


# <<31-MAY-2025:18:30>> – Adjusted unpack of run_browser_script return value
# <<31-MAY-2025:20:50>> – Added ensure_escaped_selector import and escaped selector in locator calls

# … other imports above remain unchanged …
# <<31-MAY-2025:21:45>> – Moved metadata extraction (locator.inner_text) to before navigation
# <<31-MAY-2025:21:45>> – Moved metadata extraction (locator.inner_text) to before navigation
# … other imports above remain unchanged …

async def crawl_path_from_selector(
	page,
	label,
	username,
	password,
	login_url,
	crawler_name,
	session_id,
	already_logged_in=False,
	selector=None,
	browser=None
):
	"""
	<<31-MAY-2025:16:50>> – Execute navigation, ensure single login via cookie,
	then insert parent and child DOM. Modified so that we capture parent metadata before clicking.
	"""
	debug_log("Entered crawl_path_from_selector")
	load_dotenv(verbose=True)
	writer = DBWriter("oracle_ui_dump.jsonl")

	debug_log(f"username: {username}")
	debug_log(f"login_url: {login_url}")
	debug_log(f"session_id: {session_id}")

	if selector:
		debug_log(f"🔍 Navigating to selector: {label}")
		debug_log(f"🔍 Final selector being used for navigation: {selector}")

		# 1. Escape the selector and capture its metadata BEFORE clicking
		escaped_selector = ensure_escaped_selector(selector)

		selector = ensure_escaped_selector(selector)
		debug_log(f"🔁 Ensured selector: {selector} {escaped_selector}")

		# Simplify selectors with dots
		if '\\.' in escaped_selector:
			base_sel = escaped_selector.split('\\.')[0]
		elif '.' in escaped_selector:
			base_sel = escaped_selector.split('.')[0]
		else:
			base_sel = escaped_selector
		base_sel = base_sel.replace('\\#', '#')
		if base_sel != selector:
			debug_log(f"🔄 Simplifying selector from LLM '{escaped_selector}' to '{base_sel}'")
			escaped_selector = base_sel

		if selector == ".button[title='Navigator']":
			debug_log(f"🔁 Normalizing selector at step {step_num} to a[title='Navigator']")
			escaped_selector = "a[title='Navigator']"

		if ":contains(" in selector:
			match = re.search(r":contains\((.*?)\)", selector)
			if match:
				label = match.group(1).strip("\"'")
				debug_log(f"🔁 Rewriting selector '{escaped_selector}' to text='{label}'")
				escaped_selector = f"text='{label}'"

		debug_log(f"🔁 Ensured selector in crawler (pre‐click): {escaped_selector}")
		element = page.locator(escaped_selector)
		# If this times out here, it means the parent link isn’t visible to begin with.
		label_before_click = await element.inner_text()
		aria_label = await element.get_attribute("aria-label")
		title_attr = await element.get_attribute("title")

		extracted = {
			"label": label_before_click,
			"selector": escaped_selector,
			"url": page.url,
			"category": "TBD",
			"page_id": None,
			"aria_label": aria_label,
			"title_attr": title_attr
		}

		# 2. Now run the navigation steps (click will happen here)
		steps = [
			{"action": "wait_for_selector", "selector": selector},
			{"action": "click",           "selector": selector},
			{"action": "screenshot",      "value": None},
			{"action": "log_result",      "value": None},
		]
		try:
			# ▶️ Re‐unpack run_browser_script as before
			new_page, new_browser, new_flag = await run_browser_script(
				steps=steps,
				session_id=session_id,
				login_url=login_url,
				username=username,
				password=password,
				page=page,
				browser=browser,
				already_logged_in=already_logged_in
			)
			page = new_page or page
			browser = new_browser or browser
			already_logged_in = new_flag

			# # 3. Insert the parent row now that we have metadata
			# conn = get_db_connection()
			# cur = conn.cursor()
			# cur.execute(
			# 	"""
			# 	INSERT INTO ui_paths(
			# 	  crawl_session_id, path_name, url, category,
			# 	  aria_label, title_attr, creation_date, created_by
			# 	)
			# 	VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
			# 	""",
			# 	(
			# 		session_id,
			# 		extracted["label"],
			# 		extracted["url"],
			# 		extracted["category"],
			# 		extracted["aria_label"],
			# 		extracted["title_attr"],
			# 		os.getenv("CURRENT_USER", "system")
			# 	)
			# )
			# conn.commit()

			# 4. Call extract_page_contents on the **new** page context
			path_id = extractor.insert_ui_path(
				session_id,
				path_name=extracted["label"] or "Unknown"
			)
			debug_log(f"🔁 Inserting path with ID {path_id} for session {session_id}")
			## extract page_contents inserts the ui path items
			await extractor.extract_page_contents(page, session_id, path_id)

		except Exception as e:
			debug_log(f"⚠️ Error navigating to selector: {e}")

	debug_log("Exited crawl_path_from_selector")
	# ▶️ Return page, browser, and login flag so caller can maintain session
	return page, browser, already_logged_in
