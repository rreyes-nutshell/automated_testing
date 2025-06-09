# <<08-JUN-2025:02:18>> - Unit test for selector_resolver

import pytest
from utils.selector_resolver import get_selector

def test_known_selector():
	assert get_selector("username_input") == "input[name='userid']"
	assert get_selector("export_to_excel_button") == "button:has-text('Export to Excel')"

def test_raw_selector_fallback():
	raw = "input[name='customField']"
	assert get_selector(raw) == raw
