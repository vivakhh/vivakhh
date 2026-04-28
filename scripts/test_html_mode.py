import asyncio
from playwright.async_api import async_playwright

async def test_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        
        await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
        
        # Click mode switch button
        await page.click('#editor-mode-layer-btn-open')
        await page.wait_for_timeout(500)
        
        # Click HTML mode
        await page.click('#editor-mode-html-tistory')
        await page.wait_for_timeout(500)
        
        # Now there is a CodeMirror editor. Let's see if we can paste text into it
        # The textarea is usually hidden, but CodeMirror captures input.
        # We can try to evaluate codemirror
        
        # Wait, if we use HTML mode, maybe we can just set the text in the codemirror instance?
        # Or just use page.keyboard.insert_text?
        
        # Click inside codemirror
        await page.click('.CodeMirror-scroll')
        
        # Select all and delete
        await page.keyboard.press('Meta+A')
        await page.keyboard.press('Backspace')
        
        # Insert our HTML
        test_html = "<h1>This is a real test</h1><p>It actually works!</p>"
        await page.keyboard.insert_text(test_html)
        
        await page.wait_for_timeout(1000)
        
        # Switch back to Basic mode to trigger React state update
        await page.click('#editor-mode-layer-btn-open')
        await page.wait_for_timeout(500)
        await page.click('#editor-mode-kakao-tistory')
        await page.wait_for_timeout(1000)
        
        html = await page.content()
        with open("html_test_dom.html", "w") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_html())
