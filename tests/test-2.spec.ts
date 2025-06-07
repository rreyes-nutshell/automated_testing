import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://login-ibnijb-dev1.fa.ocs.oraclecloud.com/oam/server/obrareq.cgi?encquery%3DmUDgsCHPimx73uTbba%2Frfq4CgsCDuZLrjF4Iego5fgmmZbSB0SKRpt1QrhccX%2FCRSSO0OMb6Zi5b6l0qxlze4n2jb0vfaSU133iXbd4qg%2BawpK1lQPSm%2FkReAfFxeYKXp4GY6MDPYTpRtkadi7DHA%2BqD1WoI4xNewDkNqnsmaAR8H%2Fc%2FAAyoggKN9BA7Oso3LUObZPb1gMmGHGNQOrVpAJT83ovWYy072tpZWxH0UNfX30PdNvvND9rcYX1mVx6oVNSMIrSqKz3RZICm7CWpBEUxRel0a3c2CLNWXW8TIrxMzG4uHjUg%2BSpJvfChKKvZV045dVp8e0%2BuGAvQUlphxM1zahNGPJ5yRVtIIWS1zYzfg%2FGHm%2FRUrCGxf8wWC8ii0NHY8hnPWfn8rnJOTCja2rzL9M3AWv8dZOyWn7YrSyG6gpDkRDkl0sFoavQgFAhf7boUK21k9zjXZTl0FegUi6CF1i3G8eIlFba2Jn8B3f5WOFenuXznoSHejYRQRQICgPfbzRkuDiZ9YrlRbkF6r2dQKPfidpkdLutQRbM017eM5e8qcXomgBTLPMHpfB56EGNUGubmN5LLD40subcv1eTrrT7vdF9fFP3lGSxPj12kLTqEePC%2Fgaw6Z5oNuOsTLyxFLElxm9qnJG6iyb%2BZhLmdsk322VRa6mrswHpVKI%2F%2FvNLeaxvKGeJ%2FnJYtv2NzrapxRO3zxDZS6CW1jlhUKJPY8QKtt5C8fHX9kENBJBWVw2xEW406x3r2a0kPjwHlpXTlrz1uDN6LVEzaJejN4QyvgnZNuGHZvLRiR5x3st8v0bQ1XTOJEG4jXOEPTTl0cgYNPnm5KfY8BU7uNLKtyhln4QFqJmYmR1JvCu3TAP1gCagFMwaJiKE7xU%2BLXnlUrpTJp5N6VXafAN%2BkrepAsWGfCt6nUe7UiviEGHnvJifYhuJ3efyK0QsSuiveiaGq2mv2s3YYw7cCjHCOWQR4VvhXMsSjXR31YE70pM%2Fd7S%2Bl172jsdUmtssWVZWXZ0PyP8ZtjlnPLE3ToOY658MHsnNBvwuOqoG6M58ZRAeJDTWCnTLe7K8ZRY2tpIcHelJzHB8dMYD6g7XzdlPmi8rRPR%2Fg%2Bg%2B07cGXzY8zFe53NFDRVY%2Fyjx7EkxRY%2B6j54e3p%2B69R85ZrUoc%2BpCHLz7ap5O6aaqCRHaOZqrkjnKBbsfykBxzjDgd9SwZQTf2Z2KUb%2F3QFS%2BPUNLbnofOjxQsnpvvUZ3hTUjrm3uphqDYPNrMWtHWjLdgWJmXjXg76ZBv%2BMpsnF7G54VHxxSp9%2BB5ju2evcZtIFKrtyQP4mVSNJc%2BPrAfoARQtGiAGh244rreFkC40tWSEmcta%2FASthk5F1xnBM8vkt5Odbd3PVlgACnf3UrJPx9UBkYkT4%2FusCQeDDTsVWbn1bquUSbyveepspn%2FkGXB5X4ASK%2BzgKFt%2B0Ss10tZ8kpesZJ2cJxkCg0EmCiXg%2FJgUKCbwrI9zdCjtCUkr06yN0Tve3pKjK3PH%2BNXsaJDPx8PHEUQHl5ZA4QRlkhAV8TfRAmuAPYYI6zn0XLdTLQk%2BgoYS%2Fl%2B3pbakcaTr2juuWi%2ByMHm0tUO5J%2BrieHomKJUJbEPVwKSdEKsGdLaXp8rjLsNsCN0q%2BqxHWm8THSMOlGGYMp4uwPKroXqg%20agentid%3DOraFusionApp_11AG%20ver%3D1%20crmethod%3D2%26cksum%3D6c0d59e242ff44e2ac4d7739f1b2be713dacd5d4&ECID-Context=1.006D3pJNEk6APPK6yVNa6G009dMy00074B%3BkXjE');
  await page.getByRole('textbox', { name: 'User ID' }).click();
  await page.getByRole('textbox', { name: 'User ID' }).fill('mgonzalez@mfa.org');
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('Welcome!23');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.getByRole('link', { name: 'Navigator' }).click();
  await page.getByLabel('Popup').locator('div').filter({ hasText: /^Payables$/ }).click();
  await page.getByRole('link', { name: 'Payables Dashboard' }).click();
  await page.getByRole('link', { name: 'Item: Invoices on Hold (54)' }).click();
  await page.getByRole('row', { name: 'Invoices on Hold' }).getByLabel('Select All').check();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export to Excel' }).first().click();
  const download = await downloadPromise;
  await page.getByRole('link', { name: 'Navigator' }).click();
  await page.getByRole('link', { name: 'Home' }).click();
});