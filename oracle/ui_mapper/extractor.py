from utils.logging import debug_log

async def extract_nav_metadata(page, selector, parent_label=None):
	debug_log("Entered")
	element = await page.query_selector(selector)
	if not element:
		return None

		label = (await element.inner_text()).strip()
		href = await element.get_attribute("href")
		url = href or page.url
		title_div = await page.query_selector("div.pageTitle")
		page_title = await title_div.inner_text() if title_div else None
		aria_label = await element.get_attribute("aria-label")
		title_attr = await element.get_attribute("title")

	is_actionable = bool(href and href != "#")
	page_id = f"{parent_label.lower().replace(' ', '_')}::{label.lower().replace(' ', '_')}" if parent_label else None

	entry = {
		"label": label,
		"parent_label": parent_label,
		"selector": selector,
		"action_type": "click",
		"value": None,
		"url": url,
		"category": "Navigation",
				"page_title": page_title,
				"aria_label": aria_label,
				"title_attr": title_attr,
		"is_actionable": is_actionable,
		"page_id": page_id,
	}

	# Include parent hierarchy if visible breadcrumb exists
	breadcrumbs = await page.query_selector_all("ol.breadcrumb li")
	if breadcrumbs:
		parts = []
		for crumb in breadcrumbs:
			crumb_text = await crumb.inner_text()
			parts.append(crumb_text.strip())
		if len(parts) >= 2:
			entry["parent_label"] = parts[-2]  # one level up from current

	debug_log(f"Extracted {label} with parent {entry['parent_label']}")
	debug_log("Exited")
	return entry
