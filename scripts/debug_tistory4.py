import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
        
        # Check if tinymce exists
        has_tinymce = await page.evaluate("typeof tinymce !== 'undefined'")
        print(f"Has TinyMCE: {has_tinymce}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
