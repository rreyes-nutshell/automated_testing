# at_tests/unit/test_ui_helpers.py
# <<08-JUN-2025:01:02>> - Unit tests for services.ui_helpers (stubbed Playwright).

import pytest
from services import ui_helpers as uh      # <= updated import path


# --------------------------------------------------------------------------- #
#  Playwright-like stubs
# --------------------------------------------------------------------------- #
class _FakeLocator:
	def __init__(self, *, visible=True, expanded=True, checked=False):
		self._visible  = visible
		self._expanded = expanded
		self._checked  = checked

	async def is_visible(self):          return self._visible
	async def get_attribute(self, name): return "false" if not self._expanded else "true"
	async def is_checked(self):          return self._checked

	async def click(self, timeout=0):    # toggle when representing checkbox
		self._checked = not self._checked

	async def check(self, timeout=0):    self._checked = True
	async def uncheck(self, timeout=0):  self._checked = False

	def locator(self, _):  return self   # nested locators chain
	def first(self):       return self


class _FakePage:
	def __init__(self):
		self._locators = {}

	def locator(self, selector):
		return self._locators.setdefault(selector, _FakeLocator())

	def get_by_role(self, *_ , name=None):
		return self.locator(f"role={name}")

	# Simplified Playwright stubs
	async def wait_for_selector(self, *_, **__): pass
	async def wait_for_timeout(self, *_ , **__): pass
	async def click(self, selector, timeout=0):
		await self.locator(selector).click(timeout=timeout)


# --------------------------------------------------------------------------- #
#  Tests
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_wait_for_spinner_no_spinner():
	page = _FakePage()
	await uh.wait_for_spinner(page)   # should simply return with no error


@pytest.mark.asyncio
async def test_expand_nav_panel_if_collapsed():
	page = _FakePage()
	page._locators["css=button[data-test='o-header-nav-toggle']"] = _FakeLocator(visible=True)
	await uh.expand_nav_panel_if_collapsed(page)   # must not raise


@pytest.mark.asyncio
async def test_toggle_checkbox_under_section():
	page = _FakePage()

	# Section collapsed initially
	page._locators["role=button[name='Preferences']"] = _FakeLocator(expanded=False)

	# Checkbox starts unchecked
	row_sel = "role=row >> text='Receive Email'"
	page._locators[row_sel] = _FakeLocator(checked=False)

	await uh.toggle_checkbox_under_section(
		page,
		section_label="Preferences",
		checkbox_label="Receive Email",
		selected=True,
	)

	assert page._locators[row_sel]._checked is True
