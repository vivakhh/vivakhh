import hmac
import hashlib
import time
import requests
import json
import os
import urllib.parse

class CoupangPartnersAPI:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.domain = "https://api-gateway.coupang.com"

    def _generate_hmac(self, method, url):
        datetime_kst = time.strftime('%y%m%d') + 'T' + time.strftime('%H%M%S') + 'Z'
        message = f"{datetime_kst}{method}{url}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={datetime_kst}, signature={signature}"

    def create_deeplink(self, coupang_url):
        """Generates an affiliate deeplink for a given Coupang URL"""
        method = "POST"
        url = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
        
        authorization = self._generate_hmac(method, url)
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }
        
        payload = {
            "coupangUrls": [coupang_url]
        }
        
        try:
            response = requests.post(f"{self.domain}{url}", headers=headers, data=json.dumps(payload))
            data = response.json()
            if data.get("rCode") == "0":
                return data["data"][0]["shortenUrl"]
            else:
                print(f"Coupang API Error: {data}")
                return None
        except Exception as e:
            print(f"Error creating deeplink: {e}")
            return None

if __name__ == "__main__":
    # Test execution (requires keys)
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
        
        api = CoupangPartnersAPI(
            config["coupang"]["access_key"],
            config["coupang"]["secret_key"]
        )
        print("Coupang API Module Ready.")
    else:
        print("config.json not found.")
