from fastapi import FastAPI, HTTPException, Query
import requests
import os
from typing import Optional

# ✅ Load API Key from Railway ENV (No dotenv needed)
AVE_API_KEY = os.getenv("AVE_API_KEY")
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
    return {"status": "✅ AveAI API is running", "version": "1.0.0"}

# ✅ Helper function
def fetch_ave(endpoint: str, params: Optional[dict] = None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

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
