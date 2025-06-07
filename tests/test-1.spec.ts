import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.getByRole('textbox', { name: 'User ID' }).click();
  await page.getByRole('textbox', { name: 'User ID' }).fill('');
  await page.getByRole('textbox', { name: 'User ID' }).dblclick();
  await page.getByRole('textbox', { name: 'User ID' }).fill('mfa');
  await page.getByRole('textbox', { name: 'User ID' }).click();
  await page.getByRole('textbox', { name: 'User ID' }).dblclick();
  await page.getByRole('textbox', { name: 'User ID' }).fill('mgonzalez@mfa.org');
  await page.locator('div').filter({ hasText: /^Password$/ }).click();
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('Welcome!23');
  await page.getByRole('button', { name: 'Sign In' }).click();
  page.pause();
  await page.getByText('PayablesGeneral AccountingFixed AssetsProcurementMy EnterpriseToolsOthersQuick').click();
  await page.getByRole('link', { name: 'Navigator' }).click();
  await page.locator('div').filter({ hasText: /^Payables$/ }).click();
  await page.getByRole('link', { name: 'Payables Dashboard' }).click();
  await page.getByRole('link', { name: 'Item: Rejected (109)' }).click();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export to Excel' }).first().click();
  const download = await downloadPromise;
  await page.getByRole('link', { name: 'Navigator' }).click();
  await page.getByRole('link', { name: 'Invoices' }).click();
  await page.getByRole('link', { name: 'Invoices' }).click();
});