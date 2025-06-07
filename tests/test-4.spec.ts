import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://login-ibnijb-dev1.fa.ocs.oraclecloud.com/oam/server/obrareq.cgi?encquery%3DgtkQoiJYSdnNYo1YE6r010IIjpAj5BQAmbvBx9VWBreIpXHhL2PqRSppy%2F0GCkb9Iz2jWVRza3a0RZ52M10h0fQmZRnRIBbiPVo64C1aQ9SSZSPKba1LTkGwUPt9QxnkhKcz%2F38hbiWL5YBJb8bvBmV7zKZ%2F4w2tKc1nD%2B9PTV4CfEJN3yE0ByA4IOKyRuAHhBbovMAGByZ5kHcuyspTNuRlCvl7En%2BAlcWqHqvj97UkbX41hktVea26iMNY8MRbqNlfKOXkf%2FmcRJThyffw0CeptwGo16rGrVaxuGbIY%2FG9fFj%2BfQVniNOxV7%2Bc9PpQQ7%2ByGKxTEN%2FNFTfuZmnnXPbT26sT1nokAMJNBAGTSY1pUercGp8Zp3qfSdBIT%2Bdg%2F4GOX8ty0VIGIC9crzdFtoCe0hcu86JkZLJ94Ms%2BFSTNP4b3tNhgQ3EM%2FQG9yAnmxMMXkvQUZxgrrmSr0%2FYqrBtazN%2F8lZWwek7BcXVtDJawjkC7CoCzuue%2BG3Neo4a%2Bc%2BhTWm8R1Su%2BS3Rf2GQh73QFxu3NS0AxbkC5e5TeijnrDZStudUd3H56b7emq81sDbob0oqx5bk5LKUru5SCLNj%2Bflue3lwI3js1T1waqj1EDL0eqHqBGOWXUqjI%2FYjS%2BoUzg6%2Bh1wtVtoH0qpKE2BBd0r9xIpy2KrKFcZ9gV3WyJMJjPEmvR0udL87sYLEOANG8WTONhs%2BmPhYjULmuCsPlcKBC4N5T2wKzUX6Md4TbDU%2BI3z12qN%2BTfnhbsuKzmHM2xPt70T4ry6ZtUoJgV8auxpzoBkTdZDVM1yAajL7844Yziy5GOruGjxW%2BVn1QD6fAX4HSt4ErDkvlHpJnn67%2BwIw1T1yYecUDRe432Td8RK%2B5daSYbHinN2jGTwktjKJ0rSFYJsyjKkOHPvr%2ByJhqWE%2FoFmXZPHCSIWW0aLdwIeAKvGR1vX6RzrzhhiG4NQOnyvEaswqATprLAdlcwaHKKD7NWpkXwPnfATYFRLrUXqr95uywEc3XZpVZNmYS4GJ0%2FlGtSH9uNq9j6HJg%2FrePend5NxGvMsHBd1rtSlve5g5iokMZJ7M73vF3h%2BQs5GPeNXX0xlKLZACWw3XfL5VfCO5xqZ1vVztXSRu1RaQB3q7xWPEd3rA654QUK3Yun%2F6h9SF8akd0kkvKcXZJjlDErfTQENH%2B%2FSiI1vW1wos5W0IxWFNleot97tIkBWir4Y6%2FTefBx%2B8l4MoeQxqYpHuIEDrx8J32c%2BILBLu24tx1knuhfEGEaH10wCS1QDBW32vcJ%2Bps7THeYeueHVtToPDTTX18ouhPzi4NKicBHtk5OSn77x0%2FMSX%2Fi3mybxSNWBmN6A0RxzIDkdllPHrEfsmCfoeBJRuGFLrH2NA8jPwvJFb%2BRIsTKXk3sY%2FrRGzwaX0toOJhynajViRNCia8ijvztycCc5P2H2s2gL8GDgX1SZB33oIJDOAd31EoK2c1saPenx%2BHXuN9RMOu%2Bt6Jk4RnCL6WgCmmcHZ2kDi4wgl%2BjwoheAkmNOI28PDdJTnBeE1FxU%2Fb3zI4qlNDQVriBewLQwb%2Bb%2BZ4aXUCy8jTdiQ5UgiWTZcPBUwHhyvfVwH4Yh5KYiZmWGRqpqefZTRqwdhqMpeocFFFauCHvafMfyg%3D%20agentid%3DOraFusionApp_11AG%20ver%3D1%20crmethod%3D2%26cksum%3Daa12a61c302c435bc3249be9ce830353554e41aa&ECID-Context=1.006Ddx5EcEGAPPK6yVNa6G009ujo00076s%3BkXjE');
  await page.getByRole('textbox', { name: 'User ID' }).click();
  await page.getByRole('textbox', { name: 'User ID' }).fill('mgonzalez@mfa.org');
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('Welcome!23');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.getByRole('link', { name: 'Navigator' }).click();
  await page.getByLabel('Popup').locator('div').filter({ hasText: /^Payables$/ }).click();
  await page.getByRole('link', { name: 'Payables Dashboard' }).click();
  // await page.locator('div').filter({ hasText: /^Item: Invoices on Hold \(54\)$/ }).first().click({
  //   button: 'right'
  // });
  // await page.getByRole('link', { name: 'Item: Invoices on Hold (54)' }).click();
  // await page.locator('div').filter({ hasText: /^Selected Item: Invoices on Hold \(54\)$/ }).nth(1).click();
  await page.locator('div').filter({ hasText: /^Item: Invoices on Hold \(54\)$/ }).nth(1).click();
  // await page.getByRole('link', { name: 'Selected Item: Invoices on' }).click();
  await page.locator('span').filter({ hasText: /^Select All$/ }).first().click();
  await page.getByRole('row', { name: 'Invoices on Hold' }).getByLabel('Select All').check();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export to Excel' }).first().click();
  const download = await downloadPromise;
});