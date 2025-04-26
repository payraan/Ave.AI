from fastapi import FastAPI, HTTPException, Query
import requests
from typing import Optional

# 🔐 کلید API به‌صورت هاردکد برای تست
AVE_API_KEY = "mspSf2Ai4AmgfY6qZ1B3hXEZaiM5o2tvAAA6zc5yB0ptGyxnjz841GBiHAivx8xl"

# تنظیمات اولیه
app = FastAPI(
    title="AveAI API Test",
    description="FastAPI wrapper for testing Ave.ai /tokens endpoint",
    version="1.0.0"
)

BASE_URL = "https://prod.ave-api.com/v2"
HEADERS = {
    "X-API-KEY": AVE_API_KEY,
    "Accept": "application/json",
    "User-Agent": "AveAI-Wrapper-Test"
}

# روت اصلی
@app.get("/")
def home():
    return {
        "status": "✅ AveAI API Test Server is Running",
        "version": "1.0.0"
    }

# تابع درخواست‌دهی ساده
def fetch_ave(endpoint: str, params: Optional[dict] = None):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ جستجو بر اساس نام یا سمبل یا اسمارت کانترکت
@app.get("/tokens")
def search_tokens(keyword: str = Query(..., description="Token name, symbol or address")):
    return fetch_ave("/tokens", {"keyword": keyword})

@app.get("/ranks/topics")
def get_rank_topics():
    return fetch_ave("/ranks/topics")

@app.get("/ranks")
def get_tokens_by_topic(topic: str = Query(..., description="Topic name from /ranks/topics")):
    return fetch_ave("/ranks", {"topic": topic})

@app.get("/tokens/{token_id}")
def get_token_details(token_id: str):
    return fetch_ave(f"/tokens/{token_id}")

@app.get("/klines/pair")
def get_pair_kline(pair_id: str, interval: int = 60, size: int = 10, category: str = "u"):
    return fetch_ave(f"/klines/pair/{pair_id}-solana", {
        "interval": interval,
        "size": size,
        "category": category
    })

@app.get("/klines/token")
def get_token_kline(token_id: str, interval: int = 60, size: int = 10):
    return fetch_ave(f"/klines/token/{token_id}-solana", {
        "interval": interval,
        "size": size
    })

@app.get("/tokens/top100/{token_id}")
def get_top100(token_id: str):
    return fetch_ave(f"/tokens/top100/{token_id}")

@app.get("/txs/{pair_id}")
def get_pair_txs(
    pair_id: str,
    limit: int = Query(10, description="Number of records to return"),
    to_time: Optional[int] = Query(None, description="Timestamp of latest record")
):
    params = {"limit": limit}
    if to_time:
        params["to_time"] = to_time
    return fetch_ave(f"/txs/{pair_id}", params)

@app.get("/supported_chains")
def get_supported_chains():
    return fetch_ave("/supported_chains")

# دریافت لیست روند زنجیره
@app.get("/chain_trending")
def get_chain_trending(chain_name: str = Query(..., description="Chain name to get trending tokens")):
    return fetch_ave(f"/tokens/trending", {"chain": chain_name})

