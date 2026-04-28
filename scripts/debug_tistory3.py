import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
        
        # print iframes
        frames = page.frames
        print("FRAMES:")
        for f in frames:
            print(f.name, f.url)
            
        html = await page.content()
        with open("tistory_dom.html", "w") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
