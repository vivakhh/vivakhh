import os
import argparse

def generate_spiderweb_html(target_url, title="이동 중입니다...", filename="redirect.html"):
    """
    Generates a meta-refresh / JS redirect HTML file to act as a bridge (spiderweb).
    This shields the main Tistory blog from direct external traffic sources that might
    cause low-quality flags, and allows double-dipping on ads if hosted on an ad-enabled site.
    """
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <!-- 1초 후 자동 이동 (Meta Refresh) -->
    <meta http-equiv="refresh" content="1;url={target_url}">
    <style>
        body {{
            font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
            color: #333;
        }}
        .loader {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .message {{
            font-size: 18px;
            font-weight: bold;
        }}
        .sub-message {{
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="loader"></div>
    <div class="message">안전하게 정보를 불러오는 중입니다...</div>
    <div class="sub-message">잠시만 기다려주세요. 자동으로 이동합니다.</div>
    
    <script>
        // JS Fallback Redirect
        setTimeout(function() {{
            window.location.replace("{target_url}");
        }}, 1500);
    </script>
</body>
</html>
"""
    
    # Save to file
    out_dir = "spiderwebs"
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Spiderweb redirect HTML generated at: {filepath}")
    print(f"Target URL: {target_url}")
    print("Upload this file to Google Blogspot or your custom domain (ownslp.com) to act as a traffic shield.")
    
    return filepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spiderweb Redirect HTML Generator")
    parser.add_argument("--url", type=str, required=True, help="Target Tistory or Coupang URL")
    parser.add_argument("--title", type=str, default="정보를 불러오는 중입니다...", help="Title of the redirect page")
    parser.add_argument("--out", type=str, default="redirect.html", help="Output filename")
    
    args = parser.parse_args()
    generate_spiderweb_html(args.url, args.title, args.out)
