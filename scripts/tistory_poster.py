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

    async def post_article(self, title, content_html, tags=None, publish_date=None, publish_time_str=None):
        """
        Posts an article to Tistory using the saved session.
        If publish_date (YYYY-MM-DD) and publish_time_str (HH:MM) are provided, it schedules the post.
        """
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
                # Tistory Editor uses TinyMCE
                # We can inject the HTML content directly using the TinyMCE Javascript API
                
                # Escape backticks and standard quotes for JS evaluation
                safe_html = content_html.replace('`', '\\`').replace('$', '\\$')
                await page.evaluate(f"tinymce.activeEditor.setContent(`{safe_html}`)")
                
                # Trigger React state update by interacting with the iframe directly
                frame = page.frame(name="editor-tistory_ifr")
                if frame:
                    await frame.click('body')
                    await page.keyboard.press('End')
                    await page.keyboard.press('Space')
                    await page.keyboard.press('Backspace')
                
                if tags:
                    print("Entering tags...")
                    tag_str = ", ".join(tags)
                    await page.fill('input#tagText', tag_str)
                    await page.keyboard.press('Enter')
                
                print("Publishing...")
                # Click the '완료' (Complete) button at the bottom
                await page.click('button#publish-layer-btn')
                
                # Wait for the publish layer to appear
                await page.wait_for_timeout(2000)
                
                if publish_date and publish_time_str:
                    print(f"Scheduling post for {publish_date} {publish_time_str}...")
                    # Click the '예약' (Schedule) text/radio
                    await page.get_by_text("예약", exact=True).click()
                    
                    # Wait a moment for date/time inputs to become active
                    await page.wait_for_timeout(500)
                    
                    # Fill in date and time using their classes
                    await page.fill('input.inp_date', publish_date)
                    await page.fill('input.inp_time', publish_time_str)
                    
                    # Click '예약 발행' (Schedule Publish)
                    await page.get_by_text("예약 발행", exact=True).click()
                else:
                    # Click '공개 발행' (Public Publish)
                    await page.get_by_text("공개 발행", exact=True).click()
                
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
