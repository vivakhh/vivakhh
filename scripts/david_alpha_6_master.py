import os
import json
import time
import asyncio
import google.generativeai as genai
from coupang_api import CoupangPartnersAPI
from tistory_poster import TistoryPoster

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

async def generate_article(topic, coupang_link):
    """Uses Gemini 1.5 Pro to generate a high-quality SEO article."""
    
    # Try to get API key from env
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set. Please set it.")
        return None, None, None
        
    genai.configure(api_key=api_key)
    
    # Use Gemini 1.5 Pro
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    당신은 10년 차 전문 리뷰어이자 파워블로거입니다.
    주제: "{topic}"에 관한 고품질 블로그 포스팅을 작성해주세요.
    
    [조건]
    1. 검색 엔진 최적화(SEO)를 위해 H1(제목), H2(소제목), H3 태그를 적절히 사용하세요.
    2. 서론, 본론(3개 이상의 문단), 결론으로 구성하세요.
    3. 글의 중간과 마지막 부분에 쿠팡 상품 링크를 자연스럽게 2번 삽입하세요. 
       링크 위치에는 정확히 [COUPANG_LINK_HERE] 라고 작성하세요. (제가 나중에 변환합니다)
    4. 너무 로봇 같지 않고, 친근하고 신뢰감 있는 ~요, ~다 어투를 섞어서 사용하세요.
    5. HTML 형식으로만 출력하세요. (```html 등의 마크다운 백틱은 제외하세요)
    6. 글의 첫 줄에는 다음 문구를 반드시 포함하세요: 
       <p style="font-size: 12px; color: #888;">"이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."</p>
    7. 태그(키워드)도 5~7개 추천해주세요. (맨 마지막에 쉼표로 구분하여 출력: TAGS: 태그1, 태그2...)
    """
    
    print("Generating article with Gemini...")
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # Parse output
        html_content = content
        tags = []
        
        # Extract tags
        if "TAGS:" in content:
            parts = content.split("TAGS:")
            html_content = parts[0].strip()
            tags_str = parts[1].strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            
        # Replace placeholders with real link
        if coupang_link:
            link_html = f'<div style="text-align: center; margin: 30px 0;"><a href="{coupang_link}" target="_blank" style="background-color: #0073e9; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;">최저가 확인하기</a></div>'
            html_content = html_content.replace("[COUPANG_LINK_HERE]", link_html)
            
        # Generate a catchy title (h1)
        title_prompt = f"다음 글의 제목을 클릭을 유도할 수 있도록 매력적으로 지어주세요 (글자수 30자 내외):\n\n{html_content[:500]}"
        title_response = model.generate_content(title_prompt)
        title = title_response.text.strip().replace('"', '')
        
        # Remove any leading/trailing markdown html block tags if Gemini accidentally included them
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]
            
        return title, html_content.strip(), tags
        
    except Exception as e:
        print(f"Error generating article: {e}")
        return None, None, None

async def run_engine(topic, coupang_url=None):
    print(f"\n--- Starting David Alpha 6.0 Engine for Topic: {topic} ---")
    
    config = load_config()
    
    # 1. Generate Coupang Link
    coupang_link = None
    if coupang_url and config["coupang"]["access_key"] != "YOUR_COUPANG_ACCESS_KEY":
        print("Generating Coupang Deeplink...")
        api = CoupangPartnersAPI(config["coupang"]["access_key"], config["coupang"]["secret_key"])
        coupang_link = api.create_deeplink(coupang_url)
        if coupang_link:
            print(f"Created link: {coupang_link}")
        else:
            print("Failed to create Coupang link. Proceeding without it.")
    else:
        print("Coupang API keys not configured or no URL provided. Proceeding without link.")
        
    # 2. Generate Article
    title, content, tags = await generate_article(topic, coupang_link)
    
    if not title or not content:
        print("Failed to generate article content.")
        return
        
    print(f"\n[Generated Title]: {title}")
    print(f"[Tags]: {tags}")
    print(f"[Content Length]: {len(content)} characters")
    
    # 3. Post to Tistory
    blog_name = config["tistory"]["blog_name"]
    if blog_name == "YOUR_BLOG_NAME":
        print("Tistory blog name not configured in config.json. Saving to local file instead.")
        with open(f"article_{int(time.time())}.html", "w") as f:
            f.write(f"<h1>{title}</h1>\n{content}\n<p>Tags: {tags}</p>")
        return
        
    poster = TistoryPoster(blog_name)
    success = await poster.post_article(title, content, tags)
    
    if success:
        print("Workflow completed successfully!")
    else:
        print("Workflow failed during posting.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="David Alpha 6.0 Engine")
    parser.add_argument("--topic", type=str, help="Topic for the article", required=True)
    parser.add_argument("--coupang", type=str, help="Original Coupang Product URL")
    
    args = parser.parse_args()
    
    asyncio.run(run_engine(args.topic, args.coupang))
