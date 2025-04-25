from fastapi import FastAPI, HTTPException, Query
import requests
import os
from typing import Optional

# Load environment variables
AVE_API_KEY = os.getenv("AVE_API_KEY")
if not AVE_API_KEY:
    raise RuntimeError("❌ AVE_API_KEY is not set. Please check your .env file.")

# FastAPI App Config
app = FastAPI(
    title="AveAI API",
    description="Unofficial wrapper for Ave.ai v2 endpoints",
    version="1.0.0"
)

# Constants
BASE_URL = "https://prod.ave-api.com/v2"
HEADERS = {
    "X-API-KEY": AVE_API_KEY,
    "Accept": "application/json",
    "User-Agent": "AveAI-Wrapper"
}

# Root
@app.get("/")
def home():
    return {"status": "✅ AveAI API is running", "version": "1.0.0"}

# Helper Function
def fetch_ave(endpoint: str, params: Optional[dict] = None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(response.text))

# --- API ROUTES ---

# Search for tokens by keyword
@app.get("/tokens/search")
def search_tokens(keyword: str, chain: Optional[str] = None):
    return fetch_ave("/tokens", params={"keyword": keyword, "chain": chain})

# Get token details
@app.get("/tokens/{token_id}")
def get_token_details(token_id: str):
    return fetch_ave(f"/tokens/{token_id}")

# Get top 100 holders of a token
@app.get("/tokens/top100/{token_id}")
def get_top_holders(token_id: str):
    return fetch_ave(f"/tokens/top100/{token_id}")

# Get smart contract risk report
@app.get("/contracts/{token_id}")
def get_contract_risk(token_id: str):
    return fetch_ave(f"/contracts/{token_id}")

# Get trending tokens on a specific chain
@app.get("/tokens/trending")
def get_trending_tokens(chain: str):
    return fetch_ave("/tokens/trending", params={"chain": chain})

# Get token price data (POST)
@app.get("/token-price/{token_id}")
def get_token_price(token_id: str):
    try:
        url = f"{BASE_URL}/tokens/price"
        response = requests.post(url, headers=HEADERS, json={"token_ids": [token_id]})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(response.text))

# Get rank topics
@app.get("/rank/topics")
def get_rank_topics():
    return fetch_ave("/ranks/topics")

# Get token list by topic
@app.get("/ranks/{topic}")
def get_tokens_by_topic(topic: str):
    return fetch_ave("/ranks", params={"topic": topic})

# Run on local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8290, reload=True)
