import asyncio
from playwright.async_api import async_playwright

async def delete_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        
        await page.goto("https://essay7027.tistory.com/manage/posts", wait_until="networkidle")
        
        # Look for the select all checkbox
        try:
            # Click the check-all box
            await page.click('input#inpAll')
            await page.wait_for_timeout(500)
            
            # Click delete button
            await page.click('button.btn_delete')
            
            # Confirm dialog
            page.once("dialog", lambda dialog: dialog.accept())
            await page.wait_for_timeout(2000)
            print("Successfully requested deletion of current page posts.")
        except Exception as e:
            print(f"No posts found or error deleting: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(delete_all())
