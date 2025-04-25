from fastapi import FastAPI, HTTPException, Query
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی (در حالت لوکال)
load_dotenv()

# بارگذاری کلید API از متغیر محیطی
AVE_API_KEY = os.getenv("AVE_API_KEY")
if not AVE_API_KEY or AVE_API_KEY.strip() == "":
    raise RuntimeError("❌ AVE_API_KEY is not set or is empty. Please check Railway Variables.")

# تنظیم اپلیکیشن FastAPI
app = FastAPI(
    title="AveAI API",
    description="Unofficial wrapper for Ave.ai v2 endpoints",
    version="1.0.0"
)

# تنظیمات عمومی API
BASE_URL = "https://prod.ave-api.com/v2"
HEADERS = {
    "X-API-KEY": AVE_API_KEY,
    "Accept": "application/json",
    "User-Agent": "AveAI-Wrapper"
}

# روت اصلی
@app.get("/")
def home():
    return {
        "status": "✅ AveAI API is running",
        "version": "1.0.0"
    }

# جستجوی توکن
@app.get("/tokens/search")
def search_tokens(keyword: str = Query(..., description="Search keyword")):
    endpoint = "/tokens/search"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params={"keyword": keyword})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# اطلاعات توکن با address
@app.get("/tokens/{address}")
def get_token(address: str):
    endpoint = f"/tokens/{address}"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# لیست توکن‌های ترند
@app.get("/tokens/trending")
def get_trending_tokens():
    endpoint = "/tokens/trending"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# اطلاعات Socialها
@app.get("/tokens/{address}/social")
def get_token_social(address: str):
    endpoint = f"/tokens/{address}/social"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# اطلاعات تراکنش‌ها
@app.get("/tokens/{address}/transactions")
def get_token_transactions(address: str, limit: int = 20):
    endpoint = f"/tokens/{address}/transactions"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# هولدرهای توکن
@app.get("/tokens/{address}/holders")
def get_token_holders(address: str, limit: int = 25):
    endpoint = f"/tokens/{address}/holders"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# رویدادهای توکن
@app.get("/tokens/{address}/events")
def get_token_events(address: str, limit: int = 10):
    endpoint = f"/tokens/{address}/events"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params={"limit": limit})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# اطلاعات dex
@app.get("/tokens/{address}/dex")
def get_token_dex(address: str):
    endpoint = f"/tokens/{address}/dex"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
