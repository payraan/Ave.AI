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

# ✅ Get Token Prices
@app.post("/tokens/price")
def get_token_prices(payload: Dict[str, Any] = Body(...)):
    return fetch_ave("/tokens/price", method="POST", data=payload)

# ✅ Get Token Topics
@app.get("/ranks/topics")
def get_rank_topics():
    return fetch_ave("/ranks/topics")

# ✅ Get Token List By Topic
@app.get("/ranks")
def get_tokens_by_topic(topic: str):
    return fetch_ave("/ranks", {"topic": topic})

# ✅ Get Token Details (by token-id)
@app.get("/tokens/{token_id}")
def get_token_details(token_id: str):
    return fetch_ave(f"/tokens/{token_id}")

# ✅ Get Pair Kline Data
@app.get("/klines/pair/{pair_id}")
def get_pair_kline(pair_id: str):
    return fetch_ave(f"/klines/pair/{pair_id}")

# ✅ Get Token Kline Data
@app.get("/klines/token/{token_id}")
def get_token_kline(token_id: str):
    return fetch_ave(f"/klines/token/{token_id}")

# ✅ Get Token Top100 Holders
@app.get("/tokens/top100/{token_id}")
def get_token_top_holders(token_id: str):
    return fetch_ave(f"/tokens/top100/{token_id}")

# ✅ Get Pair Txs
@app.get("/txs/{pair_id}")
def get_pair_transactions(pair_id: str):
    return fetch_ave(f"/txs/{pair_id}")

# ✅ Get Supported Chains
@app.get("/supported_chains")
def get_supported_chains():
    return fetch_ave("/supported_chains")

# ✅ Get Chain Main Tokens
@app.get("/tokens/main")
def get_chain_main_tokens(chain: str):
    return fetch_ave("/tokens/main", {"chain": chain})

# ✅ Get Chain Trending List
@app.get("/tokens/trending_by_chain")
def get_trending_by_chain(chain: str):
    return fetch_ave("/tokens/trending", {"chain": chain})

# ✅ Contract Risk Detection
@app.get("/contracts/{token_id}")
def get_contract_risk(token_id: str):
    return fetch_ave(f"/contracts/{token_id}")

