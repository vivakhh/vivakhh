import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_queries(queries, target_count=500):
    all_videos = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for query in queries:
            if len(all_videos) >= target_count:
                break
                
            url = f"https://www.youtube.com/results?search_query={query}"
            print(f"Scraping query: {query}")
            await page.goto(url)
            
            try:
                await page.wait_for_selector('ytd-video-renderer, ytd-reel-item-renderer', timeout=10000)
            except:
                continue
            
            # Scroll down to get more videos for this query
            for _ in range(20):
                await page.keyboard.press('End')
                await page.wait_for_timeout(1000)
                
                links = await page.query_selector_all('a#video-title, a.ytd-video-renderer, a.ytd-reel-item-renderer')
                for link in links:
                    href = await link.get_attribute('href')
                    if href and ('/watch?v=' in href or '/shorts/' in href):
                        full_url = f"https://www.youtube.com{href.split('&')[0]}"
                        all_videos.add(full_url)
                        if len(all_videos) >= target_count:
                            break
                
                if len(all_videos) >= target_count:
                    break
        
        video_list = list(all_videos)[:target_count]
        with open("youtube_links_500.json", "w") as f:
            json.dump(video_list, f, indent=2)
            
        print(f"Total Scraped: {len(video_list)} videos.")
        await browser.close()

if __name__ == "__main__":
    queries = [
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EC%88%98%EC%9D%B5",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EB%85%B8%ED%95%98%EC%9A%B0",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EC%87%BC%EC%B8%A0",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EA%BF%80%ED%8C%81",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EC%9E%90%EB%8F%99%ED%99%94",
        "%EC%BF%A0%ED%8C%A1+%ED%8C%8C%ED%8A%B8%EB%84%88%EC%8A%A4+%EB%A6%AC%EB%B7%B0",
        "%EC%BF%A0%ED%8C%A1+%EB%AC%BC%EA%B1%B4+%EB%A6%AC%EB%B7%B0",
        "%EC%BF%A0%ED%8C%A1+%EA%B0%80%EC%A0%84+%EB%A6%AC%EB%B7%B0",
        "%EC%BF%A0%ED%8C%A1+%EC%BA%A0%ED%95%91+%EB%A6%AC%EB%B7%B0"
    ]
    asyncio.run(scrape_queries(queries, 500))
