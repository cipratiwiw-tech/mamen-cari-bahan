from browser.launcher import launch_browser

def main():
    p, browser, page = launch_browser()
    page.goto("https://www.youtube.com")
    page.wait_for_timeout(5000)
    browser.close()
    p.stop()

if __name__ == "__main__":
    main()
