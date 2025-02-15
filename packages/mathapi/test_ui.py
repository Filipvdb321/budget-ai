from playwright.sync_api import sync_playwright
from datetime import datetime
import os

def capture_ui_state():
    print("Start UI capture...")
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created screenshots directory: {screenshots_dir}")
    
    with sync_playwright() as p:
        print("Launching Firefox...")
        browser = p.firefox.launch(
            headless=False,
            channel="firefox"  # Gebruik standaard Firefox in plaats van Nightly
        )
        context = browser.new_context()
        
        # Voeg Auth0 cookies toe
        context.add_cookies([
            {
                "name": "auth0.is.authenticated",
                "value": "true",
                "domain": "localhost",
                "path": "/"
            }
        ])
        
        page = context.new_page()
        
        try:
            url = "http://localhost:3000/"
            print(f"\nOpening homepage: {url}")
            page.goto(url)
            print("Page loaded, waiting for network idle...")
            page.wait_for_load_state("networkidle")
            
            # Debug informatie
            print("\nPage Information:")
            print(f"Title: {page.title()}")
            print("Text content of main element:")
            if page.locator("main").count() > 0:
                print(page.locator("main").first.inner_text())
            else:
                print("No main element found")
            
            # Maak screenshot met timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"{screenshots_dir}/homepage_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\nScreenshot saved: {screenshot_path}")
                
        except Exception as e:
            print(f"Error tijdens het maken van screenshots: {e}")
            raise e
        finally:
            print("\nClosing browser...")
            browser.close()

if __name__ == "__main__":
    capture_ui_state() 