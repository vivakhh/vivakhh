import asyncio
from playwright.async_api import async_playwright
import json
import os

class TistoryPoster:
    def __init__(self, blog_name):
        self.blog_name = blog_name
        self.write_url = f"https://{blog_name}.tistory.com/manage/post"
        self.state_file = f"tistory_state_{blog_name}.json"

    async def save_session(self):
        """Opens a visible browser for the user to log in and saves the session."""
        print("Opening browser for login. Please log in to Tistory (Kakao).")
        print("Close the browser manually once you see the Tistory management dashboard.")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto("https://www.tistory.com/auth/login")
            
            # Wait for the user to login and close the page
            try:
                await page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            
            # Save state
            await context.storage_state(path=self.state_file)
            print(f"Session saved to {self.state_file}")
            await browser.close()

    async def post_article(self, title, content_html, tags=None):
        """Posts an article to Tistory using the saved session."""
        if not os.path.exists(self.state_file):
            print(f"Error: {self.state_file} not found. Run save_session() first.")
            return False

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=self.state_file)
            page = await context.new_page()
            
            try:
                print(f"Navigating to {self.write_url}")
                await page.goto(self.write_url, wait_until="networkidle")
                
                # Check if we are actually logged in (if not, we'd be redirected to login)
                if "auth/login" in page.url:
                    print("Session expired or invalid. Need to log in again.")
                    return False
                
                # Handle any alert dialogs (like "You have unsaved changes")
                page.on("dialog", lambda dialog: dialog.accept())
                
                print("Entering title...")
                # Tistory Editor Title Field (New Editor)
                await page.fill('textarea.textarea_tit', title)
                
                print("Entering content...")
                # Tistory Editor uses an iframe for the rich text editor
                # We can switch to HTML mode to inject content
                
                # Click the mode switch button (기본모드 -> HTML)
                await page.click('button.btn_mode')
                await page.click('div.layer_mode button:has-text("HTML")')
                
                # Wait for HTML editor textarea
                await page.wait_for_selector('textarea.textarea_html')
                await page.fill('textarea.textarea_html', content_html)
                
                if tags:
                    print("Entering tags...")
                    tag_str = ", ".join(tags)
                    await page.fill('input.inp_tag', tag_str)
                    await page.keyboard.press('Enter')
                
                print("Publishing...")
                # Click the '완료' (Complete) button at the bottom
                await page.click('button.btn_post')
                
                # Wait for the publish layer
                await page.wait_for_selector('div.layer_post')
                
                # Click '공개 발행' (Public Publish)
                await page.click('button.btn_publish')
                
                # Wait for redirect after posting
                await page.wait_for_navigation(wait_until="networkidle")
                print("Post successful!")
                
                return True
                
            except Exception as e:
                print(f"Error during posting: {e}")
                # Save screenshot for debugging
                await page.screenshot(path="tistory_error.png")
                return False
            finally:
                await browser.close()

if __name__ == "__main__":
    # Test script usage
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
            blog_name = config["tistory"]["blog_name"]
            
            poster = TistoryPoster(blog_name)
            asyncio.run(poster.save_session())
        else:
            print("config.json not found.")
