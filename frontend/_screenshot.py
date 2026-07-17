import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:5173/", wait_until="networkidle", timeout=30000)
    time.sleep(1.5)
    page.screenshot(path="E:/FTP/terrapulse/frontend/_shot_home.png", full_page=True)

    page.goto("http://localhost:5173/map", wait_until="networkidle", timeout=30000)
    time.sleep(2.5)
    page.screenshot(path="E:/FTP/terrapulse/frontend/_shot_map.png", full_page=False)

    page.goto("http://localhost:5173/areas", wait_until="networkidle", timeout=30000)
    time.sleep(1.5)
    page.screenshot(path="E:/FTP/terrapulse/frontend/_shot_areas.png", full_page=True)

    page.goto("http://localhost:5173/search", wait_until="networkidle", timeout=30000)
    time.sleep(2.5)
    page.screenshot(path="E:/FTP/terrapulse/frontend/_shot_search.png", full_page=False)

    # mobile viewport check
    mobile = browser.new_page(viewport={"width": 375, "height": 800})
    mobile.goto("http://localhost:5173/", wait_until="networkidle", timeout=30000)
    time.sleep(1.5)
    mobile.screenshot(path="E:/FTP/terrapulse/frontend/_shot_home_mobile.png", full_page=True)

    browser.close()
print("done")
