from playwright.sync_api import sync_playwright

def get_html_website_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Scroll down to load dynamic content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)

        # Capture the HTML
        html = page.content()
        browser.close()
        return html
