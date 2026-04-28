import asyncio
from playwright.async_api import async_playwright

async def post_article():
    title = "오늘의 쿠팡 골드박스 특가! 놓치면 후회할 초특가 찬스 🎁"
    content_html = """
    <p>안녕하세요! 매일매일 찾아오는 쿠팡의 엄청난 혜택, <strong>골드박스 특가</strong> 소식을 전해드립니다.</p>
    <p>지금 바로 골드박스에서만 만날 수 있는 놀라운 할인 상품들을 확인해보세요. 로켓와우 회원이시라면 무료 배송과 반품 혜택까지 모두 누리실 수 있습니다!</p>
    <h2>🔥 오늘의 추천 특가 🔥</h2>
    <p>생필품부터 전자기기까지, 오늘만 이 가격에 판매되는 한정 수량 특가 상품들이 여러분을 기다리고 있습니다.</p>
    <p style="text-align: center;">
        <a href="https://link.coupang.com/a/ex8Hsp" target="_blank" style="display: inline-block; padding: 15px 30px; background-color: #0073e9; color: white; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 18px;">👉 지금 바로 골드박스 특가 확인하기 👈</a>
    </p>
    <p style="font-size: 12px; color: #888; margin-top: 50px;">
        이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
    </p>
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="tistory_state_essay7027.json")
        page = await context.new_page()
        
        try:
            print("Navigating to manage/post...")
            await page.goto("https://essay7027.tistory.com/manage/post", wait_until="networkidle")
            
            print("Writing title...")
            await page.fill('textarea.textarea_tit', title)
            
            print("Writing content...")
            safe_html = content_html.replace('`', '\\`').replace('$', '\\$')
            await page.evaluate(f"tinymce.activeEditor.setContent(`{safe_html}`)")
            
            print("Adding tags...")
            await page.fill('input#tagText', "쿠팡, 골드박스, 특가, 할인, 로켓배송")
            await page.keyboard.press('Enter')
            
            print("Clicking complete button...")
            await page.click('button#publish-layer-btn')
            await page.wait_for_timeout(2000)
            
            print("Clicking final publish button using text selector...")
            # Use Playwright's get_by_text for robust selection
            await page.get_by_text("공개 발행").click()
            
            await page.wait_for_timeout(3000)
            print("Success! Post published.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(post_article())
