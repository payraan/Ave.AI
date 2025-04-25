from fastapi import FastAPI, HTTPException, Query
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env (اگر وجود داشته باشد، در محیط توسعه محلی)
load_dotenv()

# ✅ چاپ اطلاعات محیطی برای دیباگ
print("PORT environment variable:", os.getenv("PORT"))
print("AVE_API_KEY exists:", "AVE_API_KEY" in os.environ)
print("AVE_API_KEY value (masked):", "***" + os.getenv("AVE_API_KEY")[-5:] if os.getenv("AVE_API_KEY") else "Not Set")

# ✅ Load API Key from Railway ENV
AVE_API_KEY = os.getenv("AVE_API_KEY")
if not AVE_API_KEY:
    print("⚠️ AVE_API_KEY is not set. Checking alternative environment variables...")
    # بررسی متغیرهایی با نام‌های مشابه برای حل مشکلات احتمالی
    for env_var in ["ave_api_key", "Ave_Api_Key", "API_KEY", "RAILWAY_AVE_API_KEY"]:
        if os.getenv(env_var):
            print(f"✅ Found alternative environment variable: {env_var}")
            AVE_API_KEY = os.getenv(env_var)
            break
    
    if not AVE_API_KEY:
        raise RuntimeError("❌ AVE_API_KEY is not set. Please check Railway Variables.")

# ✅ FastAPI App Config
app = FastAPI(
    title="AveAI API",
    description="Unofficial wrapper for Ave.ai v2 endpoints",
    version="1.0.0"
)

# ✅ Constants
BASE_URL = "https://prod.ave-api.com/v2"
HEADERS = {
    "X-API-KEY": AVE_API_KEY,
    "Accept": "application/json",
    "User-Agent": "AveAI-Wrapper"
}

# ✅ Root endpoint
@app.get("/")
def home():
    # نمایش متغیرهای محیطی در صفحه اصلی برای تشخیص مشکل
    env_vars = {
        "API_KEY_SET": AVE_API_KEY is not None,
        "API_KEY_LENGTH": len(AVE_API_KEY) if AVE_API_KEY else 0
    }
    return {
        "status": "✅ AveAI API is running", 
        "version": "1.0.0",
        "debug_info": env_vars
    }

# ✅ Helper function
def fetch_ave(endpoint: str, params: Optional[dict] = None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ API Request Failed: {str(e)}")
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_message = f"{str(e)} - Response: {e.response.text}"
        raise HTTPException(status_code=getattr(e, 'status_code', 500), detail=error_message)

# ✅ Search tokens
@app.get("/tokens/search")
def search_tokens(keyword: str, chain: Optional[str] = None):
    return fetch_ave("/tokens", params={"keyword": keyword, "chain": chain})

# ✅ Token details
@app.get("/tokens/{token_id}")
def get_token_details(token_id: str):
    return fetch_ave(f"/tokens/{token_id}")

# ✅ Top 100 holders
@app.get("/tokens/top100/{token_id}")
def get_top_holders(token_id: str):
    return fetch_ave(f"/tokens/top100/{token_id}")

# ✅ Contract risk
@app.get("/contracts/{token_id}")
def get_contract_risk(token_id: str):
    return fetch_ave(f"/contracts/{token_id}")

# ✅ Trending tokens
@app.get("/tokens/trending")
def get_trending_tokens(chain: Optional[str] = None):
    return fetch_ave("/tokens/trending", params={"chain": chain})
