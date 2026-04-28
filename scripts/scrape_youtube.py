import asyncio
from playwright.async_api import async_playwright
import json

async def scrape():
    url = "https://www.youtube.com/results?search_query=%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4&sp=EgIIBA%253D%253D"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        
        await page.wait_for_selector('ytd-video-renderer, ytd-reel-item-renderer')
        
        videos = set()
        
        # Scroll down more aggressively
        for _ in range(50):
            await page.keyboard.press('End')
            await page.wait_for_timeout(1000)
            
            links = await page.query_selector_all('a#video-title, a.ytd-video-renderer, a.ytd-reel-item-renderer')
            for link in links:
                href = await link.get_attribute('href')
                if href and ('/watch?v=' in href or '/shorts/' in href):
                    full_url = f"https://www.youtube.com{href.split('&')[0]}"
                    videos.add(full_url)
            
            if len(videos) >= 50:
                break
                
        video_list = list(videos)[:50]
        with open("youtube_links.json", "w") as f:
            json.dump(video_list, f, indent=2)
            
        print(f"Scraped {len(video_list)} videos.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
