import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
        
        # Click 기본모드
        print("Clicking 기본모드...")
        # Since there are multiple buttons with "기본모드더보기" or "기본모드", we should find the exact one.
        # usually it's the last one in the toolbar or has an id.
        await page.click('button:has-text("기본모드")')
        
        # Wait a bit
        await page.wait_for_timeout(1000)
        
        # Print HTML of layer
        layer = await page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('button, a, div')).filter(el => el.innerText && el.innerText.includes('HTML'));
            return els.map(e => e.outerHTML);
        }""")
        print("HTML BUTTONS:")
        for l in layer:
            print(l)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
