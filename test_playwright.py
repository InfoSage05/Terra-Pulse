from playwright.sync_api import sync_playwright
import urllib3
import time
urllib3.disable_warnings()

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page.goto('https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPR?OpenForm', wait_until='networkidle')
        
        page.wait_for_selector("select[name='County']", timeout=10000)
            
        page.select_option("select[name='County']", "Dublin")
        page.select_option("select[name='Year']", "2024")
        
        search_btn = page.locator("input[value='Perform Search']").first
        
        search_btn.click()
        
        print("Waiting 15 seconds for any TSPD auto-redirects...")
        time.sleep(15)
            
        html = page.content()
        with open('ppr_results.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Wrote ppr_results.html")
        browser.close()
except Exception as e:
    print(f"Error: {e}")
