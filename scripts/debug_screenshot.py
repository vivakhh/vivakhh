import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
        
        await page.click('button#publish-layer-btn')
        await page.wait_for_timeout(2000)
        await page.screenshot(path="publish_layer.png")
        
        # Save HTML too
        html = await page.content()
        with open("publish_layer_full.html", "w") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
