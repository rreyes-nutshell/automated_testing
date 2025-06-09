# ------------------------------
# dom_extractor.py
# ------------------------------

from utils.logging import debug_log

async def extract_dom_info(el):
	try:
		label_text = await el.text_content()
	except Exception as e:
		debug_log(f"⚠️ Failed to get text content: {e}")
		return {}
	label_trimmed = label_text.strip() if label_text else None
	if label_trimmed and len(label_trimmed) > 100:
		label_trimmed = label_trimmed[:100] + '...'
	tag_name = await el.evaluate("el => el.tagName.toLowerCase()")
	if tag_name in ["script", "style", "meta", "br"]:
		return {}
	classification = "button" if tag_name == "button" else "link" if tag_name == "a" else "field" if tag_name == "input" else "container"
	return {
		'label': label_trimmed,
		'tag_name': tag_name,
		'element_id': await el.get_attribute("id"),
		'class_name': await el.get_attribute("class"),
		'name_attr': await el.get_attribute("name"),
		'role': await el.get_attribute("role"),
		'aria_label': await el.get_attribute("aria-label"),
		'aria_describedby': await el.get_attribute("aria-describedby"),
		'href': await el.get_attribute("href"),
		'dest_url': await el.get_attribute("href"),
		'xpath': await el.evaluate("node => node.getAttribute('id') ? 'a#' + node.getAttribute('id').replace(/:/g, '\\:') : node.tagName.toLowerCase()"),
		'css_selector': await el.evaluate("node => node.tagName.toLowerCase() + (node.id ? '#' + node.id.replace(/:/g, '\\:') : '')"),
		'inner_text': await el.inner_text() if hasattr(el, 'inner_text') else '',
		'outer_html': await el.evaluate("node => node.outerHTML"),
		'click_action': 'click',
		'classification': classification,
		'is_clickable': True,
	}

