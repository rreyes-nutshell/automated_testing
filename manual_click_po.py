# manual_po_click.py
import asyncio
import os
from playwright.async_api import async_playwright
from oracle.login_steps import run_oracle_login_steps
from utils.logging import debug_log
from dotenv import load_dotenv



async def main(username, password, login_url):
    debug_log("Entered")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show the browser
        context = await browser.new_context()
        page = await context.new_page()

        # Reuse existing login helper
        await run_oracle_login_steps(
            page, login_url, username, password, session_id="manual_test"
        )
        debug_log("Logged in")
        # Wait for the page to load
        # Manually attempt the click
        # await page.click("text='PO Inquiry'")
        element = page.locator("a#pt1\\:_UISnvr\\:0\\:nv_itemNode_general_accounting_journals")
        # You can then interact with the element object, e.g., element.hover(), element.screenshot(), etc.
        await element.click()
        await element.scroll_into_view_if_needed()
        await element.hover()
        await page.wait_for_timeout(5000)
        await element.screenshot(path="screenshot.png") 
        # await page.click("text='PO Inquiry'", force=True)
        debug_log("Clicked PO Inquiry")
        # Wait for the page to load 
        await page.wait_for_load_state("networkidle")
        debug_log("Page loaded")
        debug_log(f"Landed on: {page.url}")
        await context.close()
        await browser.close()
        # await page.goto("https://ibnijb.fa.ocs.oraclecloud.com:443/xmlpserver/Custom/PO%20Drill%20Down/PO%20Drill%20Down%20Report.xdo?_xiasynch=&_xpf=&_xpt=0&_dFlag=false&_edIndex=0&_dIndex=0&_rToken=&_ranDiag=false&_xdo=%2FCustom%2FPO%20Drill%20Down%2FPO%20Drill%20Down%20Report.xdo&_xmode=2&xdo%3Axdo%3A_paramsREPORT_LEVEL_div_input=Header&_paramsREPORT_LEVEL=Header&xdo%3Axdo%3A_paramsP_PO_STATUS_div_input=All&_paramsP_PO_STATUS=*&xdo%3Axdo%3A_paramsP_REQ_PO_NUM_div_input=All&_paramsP_REQ_PO_NUM=*&xdo%3Axdo%3A_paramsP_INV_PO_NUM_div_input=All&_paramsP_INV_PO_NUM=*&xdo%3Axdo%3A_paramsP_SUPPLIER_div_input=All&_paramsP_SUPPLIER=*&xdo%3Axdo%3A_paramsp_project_name_div_input=All&_paramsp_project_name=*&xdo%3Axdo%3A_paramsP_PO_NUMBER_div_input=All&_paramsP_PO_NUMBER=*&xdo%3Axdo%3A_paramsP_REQUISITION_NUM_div_input=All&_paramsP_REQUISITION_NUM=*&xdo%3Axdo%3A_paramsP_INVOICE_NUM_div_input=All&_paramsP_INVOICE_NUM=*&_paramsP_CREATION_DATE=&_paramsP_CREATION_DATE_TO=&xdo%3Axdo%3A_paramsRESET_div_input=%20%20&_paramsRESET=%20%20&xdo%3Axdo%3A_paramsNew_Parameter_13_div_input=All&_paramsNew_Parameter_13=*&xdo%3Axdo%3A_paramsNew_Parameter_12_div_input=All&_paramsNew_Parameter_12=*&xdo%3Axdo%3A_paramsP_REQUESTER_div_input=All&_paramsP_REQUESTER=*&_xt=Header&_xf=analyze&_linkToReport=true")
        # await page.wait_for_url("https://ibnijb.fa.ocs.oraclecloud.com:443/xmlpserver/Custom/PO%20Drill%20Down/PO%20Drill%20Down%20Report.xdo?_xiasynch=&_xpf=&_xpt=0&_dFlag=false&_edIndex=0&_dIndex=0&_rToken=&_ranDiag=false&_xdo=%2FCustom%2FPO%20Drill%20Down%2FPO%20Drill%20Down%20Report.xdo&_xmode=2&xdo%3Axdo%3A_paramsREPORT_LEVEL_div_input=Header&_paramsREPORT_LEVEL=Header&xdo%3Axdo%3A_paramsP_PO_STATUS_div_input=All&_paramsP_PO_STATUS=*&xdo%3Axdo%3A_paramsP_REQ_PO_NUM_div_input=All&_paramsP_REQ_PO_NUM=*&xdo%3Axdo%3A_paramsP_INV_PO_NUM_div_input=All&_paramsP_INV_PO_NUM=*&xdo%3Axdo%3A_paramsP_SUPPLIER_div_input=All&_paramsP_SUPPLIER=*&xdo%3Axdo%3A_paramsp_project_name_div_input=All&_paramsp_project_name=*&xdo%3Axdo%3A_paramsP_PO_NUMBER_div_input=All&_paramsP_PO_NUMBER=*&xdo%3Axdo%3A_paramsP_REQUISITION_NUM_div_input=All&_paramsP_REQUISITION_NUM=*&xdo%3Axdo%3A_paramsP_INVOICE_NUM_div_input=All&_paramsP_INVOICE_NUM=*&_paramsP_CREATION_DATE=&_paramsP_CREATION_DATE_TO=&xdo%3Axdo%3A_paramsRESET_div_input=%20%20&_paramsRESET=%20%20&xdo%3Axdo%3A_paramsNew_Parameter_13_div_input=All&_paramsNew_Parameter_13=*&xdo%3Axdo%3A_paramsNew_Parameter_12_div_input=All&_paramsNew_Parameter_12=*&xdo%3Axdo%3A_paramsP_REQUESTER_div_input=All&_paramsP_REQUESTER=*&_xt=Header&_xf=analyze&_linkToReport=true")
    debug_log("Exited")

if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Load .env from the root
    load_dotenv(os.path.join(root_dir, '.env'))

    asyncio.run(
        main(
            username="mgonzalez@mfa.org",
            password="Welcome!23",
            login_url="https://login-ibnijb-dev1.fa.ocs.oraclecloud.com",
        )
    )
