import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://login-ibnijb-dev1.fa.ocs.oraclecloud.com/oam/server/obrareq.cgi?encquery%3DA7SSEqD1gl%2BT%2Bm0CLug%2BZK9q%2Bj5jjpijQ2Mu5sANCTbn2FrlemNJpcZbAK3aTf7dEEUeaEhTyNiGVwq6USEw4OGL72XifvCcddUwM5quf%2FzjJhbXT3X%2B9FiuYbbaSUL50We5J87hTAgWWyfHnMvMHvfpIfA55AbpoVl%2FoCqVxAl5oMpx%2BhgD3Fqn7i9IAN7fC%2FAFN5JfTN2FO%2BQuPjXLoR2Wzq03TYA1ceb8P3RzHGLRvqgOrN%2FDJ02n%2F2Rt9gSqy26B7H%2FIU%2Bk4Hg5iqNiyDrxd3PCZPO1eXi7IrKTT788rHncRUdWNQWpLJZG3AcPV96lDpClMLantV8aijZjsuirW3Yyep6iQwJaJ37LlGv82xjOzr79GhFtP%2FLmvDejEr0ouV1q6Z4EYOSWWsyLvr1X1VwtjREoZDpAcOWe0sRynvO6jI4oGJpRfLI2Z5ix9hqVKYaCnD9lhGY7HBf3ZzAYxPXjSOVOyIGm4BLhpUBGagxX7YMT21Ns24zM3Q%2BN%2BytQSbOpbDAtDtEXO81FBvUPgOczyBlIUJOfhMw5v42XPOIODncVibw%2FXHRz3OtI3UO%2FAwoqDyT5%2BZxcXdzvNCoQWAMGvIugrRuCQf3DxpN4P10O8LfqcKSmUh30yUJ2y%2B13rXVox6K63fsjYmQR9gU37pR3yY1yUX8RVkXPtc5GMQXSL5Az4oeeNAKMM3KaVL9Xul2a%2BUG3TPRk0MILp9LQ%2Fiv0R47x0GSbcH7fQilNCnU4eLyF%2Fm89ifj3624t765BZH%2F58ngpMDpnY7TwHLZi8Ej7rc%2FX5RPMZP2tZsbFkANiDpRDyo%2Fp2imPBlxeJlTNqyGCYfYYk4etxKA6qhRhgmCdm%2Fsr3LkCMpZGs3FlsqcBFeTCywEZe78WC%2Fp2ASspsiFu%2F%2FnXVyeXP11eswAGm5rKZhScLxFpaxdlJJVNOcEMCn%2BG3I%2FXk%2BgwsKx%2F1%2FPLsIg%2F9kOnCpKzeHGnNVIpop8PWqHVGC6HAi8zSHVw%2F9aY5itvepQvcCxoR8kavui8UfT1JXr0xu49zoCoMi%2BxaCa86%2BQ37IV9XOL7r6cwHcHLYiRC2%2FCFia6Yq7gqwdRlwHLq6r8vQGo%2FY9VAo9uihu5BCg3BYFTV%2FA9NrGcR2N8wdXpH3THssI5Rp2vTCMqEd6pAMmY%2Bl%2BM1W0OYHvW99kqf130vkoT6qjQbMG4B360ZnAndkOIXIaR0O%2FzzzWnjsPPmB5JxClqcZM3NfhQHUqRtRK5Im5mhcgb8j5qT96pY0%2F0SpxN9vZ%2FiCdFNVOCiKQUA7nhhg2Ck7fa3bPKD6tJ6p8jywSZEbwYqVYbMTtT9NBwabKj04hoKe%2Bdvx%2Fd2Z2XpwoYh2eIJrjs5KI76svXibWquiUgVeNYkAsGlW6VoGgT8gZsCi%2Bp9NXexvcZfNhgq6e%2FABG6o767UPeXEoIP1XfFQudRkfjqHo7SwoIXoQMV4yNcMn%2BL%2FXv15Zd2z25JTBHa4U2xbHnYwuIwLTK5TMwcjzVwl407FHJ%2FFP6ADMxAeTnFwCZTvla%2FjJtimwOE9wGx6WWGDZp7RcqxFkj6RHOhh%2B1cLm%2BBe%2FWDjIcEoGkBDuxF8N0aLQ%2BuFB3Xem7sYAqbMh%2F9Arcm%2BKA%2FWHECqKpEfVYwysIGkyKeMxEP2Kjq7ZNHiQBkahhsV2gxg7skbhbIPDpK3iLqU5%2BQ%3D%3D%20agentid%3DOraFusionApp_11AG%20ver%3D1%20crmethod%3D2%26cksum%3D5b059b8ad39383a07e72ff6c1b0c51b92530c179&ECID-Context=1.006DdvCbYAnAPPK6yVNa6G009ujo0006Ef%3BkXjE")
    page.get_by_role("textbox", name="User ID").click()
    page.get_by_role("textbox", name="User ID").fill("mgonzalez@mfa.org")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("Welcome!23")
    page.get_by_role("button", name="Sign In").click()
    page.get_by_role("link", name="Navigator").click()
    page.locator("div").filter(has_text=re.compile(r"^Payables$")).click()
    page.get_by_role("link", name="Payables Dashboard").click()
    page.locator("div").filter(has_text=re.compile(r"^Item: Invoices on Hold \(54\)$")).nth(1).click()
    page.get_by_role("row", name="Invoices on Hold").get_by_label("Select All").check()
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Export to Excel").first.click()
    download = download_info.value

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
