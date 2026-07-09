from playwright.sync_api import sync_playwright
import time
import os

print("Starting Playwright download test...")

try:
    with sync_playwright() as p:
        # Launch Chromium headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        url = 'https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPRDownloads?OpenForm'
        print("Navigating to:", url)
        page.goto(url, wait_until='networkidle')
        
        # Wait for county select
        print("Waiting for County selector...")
        page.wait_for_selector("select[name='County']", timeout=10000)
        
        # Select Dublin, 2024, All Months
        print("Selecting form options...")
        page.select_option("select[name='County']", "Dublin")
        page.select_option("select[name='Year']", "2024")
        page.select_option("select[name='Month']", "ALL")
        
        # Expect download
        print("Clicking Perform Download and expecting download...")
        with page.expect_download(timeout=30000) as download_info:
            page.locator("input[value='Perform Download']").click()
        
        download = download_info.value
        path = download.path()
        print("Downloaded file path:", path)
        print("Suggested filename:", download.suggested_filename)
        
        output_file = "dublin_2024_test.csv"
        download.save_as(output_file)
        print(f"Saved download to {output_file}, size: {os.path.getsize(output_file)} bytes")
        
        # Read first few lines of the file to see the headers and content
        with open(output_file, 'r', encoding='cp1252') as f:
            print("First 3 lines of CSV:")
            for _ in range(3):
                print(f.readline().strip())
                
        browser.close()
        
except Exception as e:
    print(f"Error during Playwright download: {e}")
