from fastapi import FastAPI, HTTPException, Query
import requests
from typing import Optional

# ✅ هاردکد کردن کلید API (فقط برای تست – امن نیست برای تولید!)
AVE_API_KEY = "ytuy8mznKhFmJWyMzEV7YsoaYoHrgLHxB30xOl1gycoGfmezc3eq4KdR9nb136Vc"

# ✅ Base settings
app = FastAPI(
    title="AveAI API",
    description="Unofficial wrapper for Ave.ai v2 endpoints",
    version="1.0.0"
)

BASE_URL = "https://prod.ave-api.com/v2"
HEADERS = {
    "X-API-KEY": AVE_API_KEY,
    "Accept": "application/json",
    "User-Agent": "AveAI-Wrapper"
}

# ✅ Root endpoint
@app.get("/")
def home():
    return {
        "status": "✅ AveAI API is running",
        "version": "1.0.0",
        "debug": "🔐 API Key is hardcoded for test"
    }

# ✅ Utility function
def fetch_ave(endpoint: str, params: Optional[dict] = None):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Endpoint: Search Tokens
@app.get("/tokens/search")
def search_token(keyword: str):
    return fetch_ave("/tokens/search", {"keyword": keyword})

# ✅ Endpoint: Trending Tokens
@app.get("/tokens/trending")
def trending_tokens():
    return fetch_ave("/tokens/trending")

# ✅ Endpoint: Token Info by Address
@app.get("/token/{address}")
def token_info(address: str):
    return fetch_ave(f"/token/{address}")

# ✅ Endpoint: Token Holders
@app.get("/token/{address}/holders")
def token_holders(address: str, page: int = 1, limit: int = 10):
    return fetch_ave(f"/token/{address}/holders", {"page": page, "limit": limit})

# ✅ Endpoint: Token Transfers
@app.get("/token/{address}/transfers")
def token_transfers(address: str, page: int = 1, limit: int = 10):
    return fetch_ave(f"/token/{address}/transfers", {"page": page, "limit": limit})

# ✅ Endpoint: Token Anomalies
@app.get("/token/{address}/anomalies")
def token_anomalies(address: str):
    return fetch_ave(f"/token/{address}/anomalies")
