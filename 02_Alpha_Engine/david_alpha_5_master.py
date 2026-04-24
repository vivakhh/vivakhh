#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Alpha 5.0 - OwnSLP.com 쿠팡 수익화 자동화 엔진
개선 버전: 보안 강화 + 안정성 + 품질 향상
"""

import os
import json
import logging
import re
import requests
from datetime import datetime, timezone
import vertexai
from vertexai.generative_models import GenerativeModel
from flask import Flask, jsonify, request

# ─────────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 설정 로드
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "ownslp_config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# 🔐 보안: 비밀번호는 환경변수에서 가져옴 (config.json에 절대 저장 금지)
WP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
if not WP_PASSWORD:
    raise RuntimeError("❌ 환경변수 WP_APP_PASSWORD가 설정되지 않았습니다. Cloud Run 환경변수를 확인하세요.")

PROJECT_ID = CONFIG["cloud"]["project_id"]
vertexai.init(project=PROJECT_ID, location="us-central1")

# ─────────────────────────────────────────────
# 쿠팡 배너 HTML 생성
# ─────────────────────────────────────────────
def get_synergy_html() -> str:
    """포스팅 최상단에 수익형 배너 배치"""
    m = CONFIG["monetization"]
    return f'''
<div style="background:#ffffff;border:3px solid #ef4444;border-radius:20px;padding:30px;margin:0 0 40px 0;text-align:center;box-shadow:0 15px 30px rgba(239,68,68,0.15);">
    <h3 style="color:#ef4444;margin-top:0;font-size:22px;font-weight:800;">🥇 데이빗 오빠의 '{m["product_label"]}' 추천</h3>
    <p style="color:#334155;font-size:17px;">
        <b>{m["target_product"]}</b>! 제가 직접 골랐습니다. 품질 보증!<br>
        지금 최저가 혜택을 직접 확인해보세요.
    </p>
    <div style="margin:25px 0;">
        <a href="{m["product_link"]}" target="_blank" rel="noopener">
            <img src="{m["product_img"]}" alt="{m["target_product"]}" width="200" style="border-radius:12px;">
        </a>
    </div>
    <a href="{m["product_link"]}" target="_blank" rel="noopener"
       style="display:inline-block;background:#ef4444;color:#fff!important;padding:18px 50px;border-radius:50px;text-decoration:none;font-weight:900;font-size:20px;">
        혜택 확인하기 ▶
    </a>
    <p style="font-size:12px;color:#94a3b8;margin-top:25px;">{CONFIG["coupang"]["disclosure_text"]}</p>
</div>
<hr style="border:0;height:1px;background:#e2e8f0;margin-bottom:40px;">
'''

# ─────────────────────────────────────────────
# AI 응답 정제 (마크다운 코드블록 제거)
# ─────────────────────────────────────────────
def clean_ai_response(raw: str) -> str:
    """Gemini가 ```html ... ``` 로 감싸서 응답할 경우 HTML만 추출"""
    raw = raw.strip()
    # ```html ... ``` 또는 ``` ... ``` 패턴 제거
    match = re.search(r"```(?:html)?\s*([\s\S]*?)```", raw)
    if match:
        return match.group(1).strip()
    return raw

# ─────────────────────────────────────────────
# AI 원고 생성
# ─────────────────────────────────────────────
def generate_content(topic: str) -> dict:
    """
    Gemini로 제목 + 본문 HTML 동시 생성
    Returns: {"title": str, "body_html": str}
    """
    persona = CONFIG["ai"]["persona"]
    model_name = CONFIG["ai"].get("gemini_model", "gemini-1.5-flash")
    model = GenerativeModel(model_name)

    prompt = f"""당신은 '{persona}'입니다.
아래 주제로 블로그 포스팅을 작성하세요.

[주제]: {topic}

[반드시 지켜야 할 형식]
- 첫 줄: JSON 한 줄 → {{"title": "SEO에 최적화된 매력적인 제목"}}
- 이후: 본문 HTML (h2, h3, p, ul 태그 사용)
- 분량: 최소 2,500자 이상
- 볼드체: ** 별표 사용 절대 금지, <b> 태그만 사용
- 말투: 따뜻하고 전문적인 재활 전문가의 어투
- 마지막 문단: 독자 응원 메시지로 마무리

[절대 포함 금지]
- 마크다운 코드블록(```html)
- 외부 링크 (쿠팡 링크 제외)
"""

    logger.info(f"[AI] 원고 생성 시작: {topic}")
    res = model.generate_content(prompt)
    raw = res.text.strip()

    # 첫 줄에서 title JSON 파싱 시도
    lines = raw.split("\n", 1)
    title = topic  # fallback
    body_html = raw

    try:
        first_line = lines[0].strip()
        # JSON 파싱
        title_data = json.loads(first_line)
        title = title_data.get("title", topic)
        body_html = lines[1].strip() if len(lines) > 1 else raw
    except (json.JSONDecodeError, IndexError):
        logger.warning("[AI] 제목 JSON 파싱 실패 → topic을 제목으로 사용")

    body_html = clean_ai_response(body_html)

    # 최소 분량 체크
    text_only = re.sub(r"<[^>]+>", "", body_html)
    char_count = len(text_only)
    logger.info(f"[AI] 생성 완료: 제목='{title}', 글자수={char_count}")

    if char_count < 1_500:
        raise ValueError(f"생성된 본문이 너무 짧습니다 ({char_count}자). 재시도가 필요합니다.")

    return {"title": title, "body_html": body_html}

# ─────────────────────────────────────────────
# 워드프레스 발행
# ─────────────────────────────────────────────
def publish_to_wordpress(title: str, html_content: str) -> str:
    """워드프레스 REST API로 포스팅 발행. 성공 시 URL 반환"""
    site = CONFIG["site"]
    endpoint = f"{site['url']}/wp-json/wp/v2/posts"

    payload = {
        "title": title,
        "content": html_content,
        "status": "publish",
        "author": site["author_id"],
    }

    logger.info(f"[WP] 발행 시작: '{title}'")
    r = requests.post(
        endpoint,
        json=payload,
        auth=(site["username"], WP_PASSWORD),
        timeout=30,
    )

    # HTTP 에러 즉시 예외 처리
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"워드프레스 발행 실패 (HTTP {r.status_code}): {r.text[:300]}") from e

    result = r.json()
    post_url = result.get("link")
    if not post_url:
        raise RuntimeError(f"발행 응답에 URL 없음: {result}")

    logger.info(f"[WP] 발행 완료: {post_url}")
    return post_url

# ─────────────────────────────────────────────
# 슬랙 완료 알림 (선택)
# ─────────────────────────────────────────────
def notify_slack(title: str, post_url: str) -> None:
    """슬랙 웹훅으로 발행 완료 알림 (환경변수 없으면 스킵)"""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message = {
        "text": f"✅ *새 포스팅 발행 완료*\n제목: {title}\n링크: {post_url}\n시각: {now}"
    }
    try:
        requests.post(webhook_url, json=message, timeout=10)
        logger.info("[Slack] 알림 발송 완료")
    except Exception as e:
        logger.warning(f"[Slack] 알림 실패 (무시): {e}")

# ─────────────────────────────────────────────
# 메인 작업 흐름
# ─────────────────────────────────────────────
def run_job(topic: str) -> dict:
    """전체 파이프라인: AI 생성 → 배너 결합 → WP 발행 → 슬랙 알림"""
    try:
        # 1. AI 원고 생성
        content = generate_content(topic)

        # 2. 쿠팡 배너 + 본문 결합
        final_html = get_synergy_html() + content["body_html"]

        # 3. 워드프레스 발행
        post_url = publish_to_wordpress(content["title"], final_html)

        # 4. 슬랙 알림
        notify_slack(content["title"], post_url)

        return {
            "status": "success",
            "title": content["title"],
            "link": post_url,
        }

    except Exception as e:
        logger.error(f"[ERROR] run_job 실패: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

# ─────────────────────────────────────────────
# Flask 앱
# ─────────────────────────────────────────────
app = Flask(__name__)

@app.route("/health")
def health():
    """Cloud Run 헬스체크용"""
    return jsonify({"status": "ok", "version": "5.0"})

@app.route("/trigger")
def trigger():
    """
    GET /trigger?topic=주제명
    topic 미입력 시 기본 주제로 실행
    """
    topic = request.args.get("topic", "").strip()
    if not topic:
        topic = "재활의 기적을 만드는 실전 가이드"
    return jsonify(run_job(topic))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
