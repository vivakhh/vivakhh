import asyncio
from tistory_poster import TistoryPoster

title = "요즘 서울 날씨 쌀쌀하죠? 관절 영양제 진짜 필수입니다 (최저가 구매 팁)"

content_html = """
<h2>서울의 갑작스러운 추위, 욱신거리는 무릎 통증의 원인</h2>
<p>최근 서울 날씨가 급격히 추워지면서 찬 바람이 불기 시작했습니다. 이럴 때일수록 우리 몸의 관절은 뻣뻣해지고, 계단을 오르내릴 때마다 시큰거리는 통증을 호소하시는 분들이 정말 많습니다. 저 역시 서울에 살면서 겨울이 다가올 때마다 무릎이 시려서 밤잠을 설치곤 했습니다.</p>

<h2>나만 아픈 게 아닙니다, 방치하면 더 큰 돈 듭니다</h2>
<p>관절 연골은 한 번 닳기 시작하면 자연적으로 재생되지 않습니다. '조금 쉬면 나아지겠지' 하고 방치하다가 나중에 병원비로 수백만 원이 깨지는 경우가 허다합니다. 부모님께서 무릎이 아프다고 말씀하시기 전에 미리미리 챙겨드려야 하는 이유입니다.</p>

<h2>식약처 인증 관절 영양제로 연골 꽉 채우기</h2>
<p>관절 건강에는 연골의 주요 성분인 콘드로이친과 MSM(식이유황)이 듬뿍 들어간 영양제가 직빵입니다. 꾸준히 드시면 뻣뻣했던 무릎이 부드러워지고, 아침에 일어날 때의 뻐근함이 확실히 줄어드는 것을 느끼실 수 있습니다.</p>
<div style="text-align: center; margin: 30px 0;"><a href="https://link.coupang.com/a/ex8Hsp" target="_blank" style="background-color: #e52528; color: white; padding: 18px 36px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block;">🔥 지금 당장 최저가 확인하기 (매진 임박)</a></div>

<h2>지금이 아니면 품절됩니다</h2>
<p>현재 날씨가 추워지면서 관절 영양제 주문량이 폭주하고 있습니다. 특히 가장 효과가 좋은 제품들은 벌써 품절 대란이 일어나고 있어, 지금 구매하지 않으시면 가격이 오르거나 한참을 기다리셔야 할 수도 있습니다.</p>

<h2>무릎 통증, 더 이상 참지 마세요</h2>
<p>하루라도 빨리 드시는 것이 남는 장사입니다. 부모님 선물용으로도 좋고, 나를 위한 투자로도 완벽합니다. 지금 바로 아래 링크를 통해 가장 혜택이 좋은 제품을 확인해 보세요!</p>
<div style="text-align: center; margin: 30px 0;"><a href="https://link.coupang.com/a/ex8Hsp" target="_blank" style="background-color: #e52528; color: white; padding: 18px 36px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block;">🔥 지금 당장 최저가 확인하기 (매진 임박)</a></div>

<p style="font-size: 11px; color: #999; text-align: center; margin-top: 50px;">"이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."</p>
"""

tags = ["관절영양제", "관절약", "무릎통증", "콘드로이친", "부모님선물"]

async def main():
    print("Testing Tistory Poster with hardcoded article...")
    poster = TistoryPoster("essay7027")
    
    # Schedule for tomorrow 09:00
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    
    # Call post
    success = await poster.post_article(title, content_html, tags, publish_date=date_str, publish_time_str="09:00")
    if success:
        print("Test post scheduled successfully!")
    else:
        print("Failed to post.")

if __name__ == "__main__":
    asyncio.run(main())
