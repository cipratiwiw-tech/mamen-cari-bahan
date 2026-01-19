from playwright.sync_api import sync_playwright

def launch_browser(headless=False):
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=headless,
        slow_mo=50
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    return p, browser, page
