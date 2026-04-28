import os
import json
import time
import asyncio
from datetime import datetime, timedelta
import google.generativeai as genai
from coupang_api import CoupangPartnersAPI
from tistory_poster import TistoryPoster

# 아로스 방식 지역명 리스트 (예시: 17개 광역지자체 + 주요 도시)
REGIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", 
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    "강남", "서초", "송파", "해운대", "분당", "판교", "일산", "동탄"
]

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

async def generate_pasona_article(base_topic, region, coupang_link, config):
    """Uses Gemini 1.5 Pro to generate a PASONA-framed article localized by region."""
    
    api_key = config.get("ai", {}).get("gemini_api_key")
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        
    if not api_key:
        print("GEMINI_API_KEY is not set in config.json or environment variables. Please set it.")
        return None, None, None
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # PASONA: Problem, Affinity, Solution, Offer, Narrowing down, Action
    prompt = f"""
    당신은 블로그 마케팅 전문가이자 카피라이터입니다.
    키워드: "{region} {base_topic}"
    
    위 키워드를 바탕으로 PASONA 법칙을 적용하여 완벽한 블로그 포스팅을 작성해주세요.
    
    [PASONA 법칙 구조]
    1. Problem (문제 제기): {region}에 거주하는 타겟 독자가 공감할 만한 심각한 문제나 고통을 제시하세요. (예: "요즘 {region} 날씨가 추워지면서 관절 통증을 호소하는 분들이 급증하고 있습니다.")
    2. Affinity (친근감/공감): 독자의 고통에 깊이 공감하며, 나(필자)도 같은 경험이 있거나 깊이 이해하고 있음을 어필하세요.
    3. Solution (해결책 제시): 이 문제를 해결할 수 있는 명확한 방법이나 상품의 효능을 제시하세요.
    4. Offer (제안): 구체적인 해결 수단(상품)을 소개하고, 이 글을 읽는 사람에게만 주어지는 혜택을 강조하세요.
    5. Narrowing down (제한): "재고가 얼마 안 남았다", "지금 안 사면 가격이 오른다", "당장 신청 안 하면 손해다" 등의 제한(긴급성)을 두어 공포심과 조급함을 자극하세요.
    6. Action (행동 촉구): 아래 링크를 눌러 당장 행동(구매/신청)하도록 유도하세요.
    
    [조건]
    1. 검색 엔진 최적화(SEO)를 위해 H2, H3 태그를 사용하세요. (H1은 제외)
    2. 글의 내용 중에 [COUPANG_LINK_HERE] 를 정확히 2번 넣으세요. (Action 부분과 Solution 부분)
    3. 대가성 문구는 절대로 첫 줄에 쓰지 말고, 글의 **맨 마지막 줄**에 아래 HTML로 삽입하세요:
       <p style="font-size: 11px; color: #999; text-align: center; margin-top: 50px;">"이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."</p>
    4. HTML 형식으로만 출력하세요. (```html 마크다운 제외)
    5. 마지막 줄 다음엔 TAGS: 태그1, 태그2 형식으로 5개 추천.
    """
    
    print(f"Generating article for {region}...")
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # Parse output
        html_content = content
        tags = []
        
        if "TAGS:" in content:
            parts = content.split("TAGS:")
            html_content = parts[0].strip()
            tags_str = parts[1].strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            
        # Replace placeholders with real link and nice button styling
        if coupang_link:
            link_html = f'<div style="text-align: center; margin: 30px 0;"><a href="{coupang_link}" target="_blank" style="background-color: #e52528; color: white; padding: 18px 36px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block;">🔥 지금 당장 최저가 확인하기 (매진 임박)</a></div>'
            html_content = html_content.replace("[COUPANG_LINK_HERE]", link_html)
            
        # Generate Title
        title_prompt = f"다음 글의 제목을 클릭률이 폭발하도록 짓되, 반드시 '{region}'과 '{base_topic}'이라는 단어가 포함되게 해주세요 (30자 내외):\n\n{html_content[:500]}"
        title_response = model.generate_content(title_prompt)
        title = title_response.text.strip().replace('"', '').replace("'", "")
        
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]
            
        return title, html_content.strip(), tags
        
    except Exception as e:
        print(f"Error generating article for {region}: {e}")
        return None, None, None

def get_next_schedule_times(start_date, count, posts_per_day=4):
    """Generates a list of (date_str, time_str) for scheduling."""
    # Assuming times: 08:00, 12:00, 18:00, 22:00
    times_pool = ["08:00", "12:00", "18:00", "22:00"]
    schedules = []
    
    current_date = start_date
    for i in range(count):
        day_offset = i // posts_per_day
        time_index = i % posts_per_day
        
        target_date = current_date + timedelta(days=day_offset)
        date_str = target_date.strftime("%Y-%m-%d")
        time_str = times_pool[time_index]
        
        schedules.append((date_str, time_str))
        
    return schedules

async def run_mass_engine(base_topic, coupang_url, num_posts=5):
    print(f"\n--- Starting David Alpha 7.0 Mass Engine ---")
    print(f"Base Topic: {base_topic}")
    print(f"Target Posts: {num_posts}")
    
    config = load_config()
    
    # 1. Generate Coupang Link (Only once)
    coupang_link = None
    if coupang_url:
        if "link.coupang.com" in coupang_url or config["coupang"]["access_key"] == "YOUR_COUPANG_ACCESS_KEY" or not config["coupang"]["access_key"]:
            # If it's already a short link OR no API key is configured, use it directly
            coupang_link = coupang_url
            print(f"Using provided Coupang link directly (API bypass): {coupang_link}")
        else:
            api = CoupangPartnersAPI(config["coupang"]["access_key"], config["coupang"]["secret_key"])
            coupang_link = api.create_deeplink(coupang_url)
            print(f"Generated Coupang Link via API: {coupang_link}")
    
    blog_name = config["tistory"]["blog_name"]
    poster = TistoryPoster(blog_name)
    
    # Get schedule times starting from tomorrow
    start_date = datetime.now() + timedelta(days=1)
    schedules = get_next_schedule_times(start_date, num_posts)
    
    regions_to_use = REGIONS[:num_posts]
    
    for i, region in enumerate(regions_to_use):
        date_str, time_str = schedules[i]
        print(f"\n[{i+1}/{num_posts}] Generating for Region: {region} (Schedule: {date_str} {time_str})")
        
        title, content, tags = await generate_pasona_article(base_topic, region, coupang_link, config)
        if not title:
            continue
            
        print(f"Title: {title}")
        
        # Post (Scheduled)
        if blog_name != "YOUR_BLOG_NAME":
            success = await poster.post_article(title, content, tags, publish_date=date_str, publish_time_str=time_str)
            if success:
                print("Scheduled successfully.")
            else:
                print("Failed to schedule.")
        else:
            print("Blog name not configured. Skipping actual posting.")
        
        # Delay to avoid API rate limits
        await asyncio.sleep(5)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="David Alpha 7.0 Mass Engine")
    parser.add_argument("--topic", type=str, required=True, help="Base topic (e.g. '관절 영양제 추천')")
    parser.add_argument("--coupang", type=str, help="Coupang Product URL")
    parser.add_argument("--count", type=int, default=5, help="Number of region-based posts to generate")
    
    args = parser.parse_args()
    asyncio.run(run_mass_engine(args.topic, args.coupang, args.count))
