from fastapi import FastAPI, HTTPException, Query, Depends
import aiohttp
import logging
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Union

# تنظیم لاگینگ برای مشاهده خطاهای دقیق
logging.basicConfig(level=logging.DEBUG)

# بارگذاری متغیرهای محیطی
load_dotenv()

# 🔐 کلید API از متغیر محیطی یا مقدار پیش‌فرض
AVE_API_KEY = os.getenv("AVE_API_KEY", "mspSf2Ai4AmgfY6qZ1B3hXEZaiM5o2tvAAA6zc5yB0ptGyxnjz841GBiHAivx8xl")

# تنظیمات اولیه
app = FastAPI(
    title="AveAI API",
    description="FastAPI wrapper for Ave.ai cryptocurrency data services",
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
        "status": "✅ AveAI API Server is Running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# برای تست ساده API
@app.get("/test")
def test():
    return {"status": "ok", "message": "Test endpoint is working"}

# تابع درخواست‌دهی غیرهمزمان
async def fetch_ave(endpoint: str, params: Optional[dict] = None):
    try:
        async with aiohttp.ClientSession() as session:
            logging.debug(f"Requesting {BASE_URL}{endpoint} with params {params}")
            async with session.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params) as response:
                status = response.status
                logging.debug(f"Status code: {status}")
                response_text = await response.text()
                logging.debug(f"Response: {response_text[:500]}")
                
                if status >= 400:
                    error_msg = f"API Error: {response_text}"
                    logging.error(error_msg)
                    raise HTTPException(status_code=status, detail=error_msg)
                
                return await response.json()
    except aiohttp.ClientError as e:
        error_msg = f"Client Error: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# ✅ جستجو بر اساس نام یا سمبل یا اسمارت کانترکت
@app.get("/tokens", tags=["Tokens"])
async def search_tokens(
    keyword: str = Query(..., description="Token name, symbol or address"),
    chain: Optional[str] = Query(None, description="Blockchain name (optional)")
):
    """
    Search for tokens by name, symbol or contract address.
    Returns a list of matching tokens.
    """
    params = {"keyword": keyword}
    if chain:
        params["chain"] = chain
    
    response = await fetch_ave("/tokens", params)
    
    # استخراج داده‌های توکن از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه محدود جستجوی توکن برای GPT
@app.get("/tokens/limited", tags=["GPT Optimized"])
async def search_tokens_limited(
    keyword: str = Query(..., description="Token name, symbol or address"),
    chain: Optional[str] = Query(None, description="Blockchain name (optional)"),
    limit: int = Query(5, description="Maximum number of results to return")
):
    """
    Search for tokens with limited results (GPT-optimized).
    Returns a limited list of matching tokens.
    """
    params = {"keyword": keyword}
    if chain:
        params["chain"] = chain
    
    response = await fetch_ave("/tokens", params)
    
    # استخراج و محدود کردن داده‌های توکن از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"][:limit]
    return response

@app.get("/ranks/topics", tags=["Rankings"])
async def get_rank_topics():
    """
    Get available ranking topics that can be used with the /ranks endpoint.
    """
    response = await fetch_ave("/ranks/topics")
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        # برگرداندن فقط آیدی‌های موضوعات
        topics = [topic["id"] for topic in response["data"]]
        return topics
    return response

@app.get("/ranks", tags=["Rankings"])
async def get_tokens_by_topic(
    topic: str = Query(..., description="Topic name from /ranks/topics")
):
    """
    Get ranked tokens by specified topic.
    Use /ranks/topics to get available topics.
    """
    response = await fetch_ave("/ranks", {"topic": topic})
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه محدود رتبه‌بندی برای GPT
@app.get("/ranks/limited", tags=["GPT Optimized"])
async def get_tokens_by_topic_limited(
    topic: str = Query(..., description="Topic name from /ranks/topics"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Get ranked tokens by specified topic with limited results (GPT-optimized).
    Use /ranks/topics to get available topics.
    """
    response = await fetch_ave("/ranks", {"topic": topic})
    
    # استخراج و محدود کردن داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"][:limit]
    return response

@app.get("/tokens/{token_id}", tags=["Tokens"])
async def get_token_details(token_id: str):
    """
    Get detailed information about a specific token.
    Format should be {token}-{chain}, e.g., 0x05ea8779...baefd-bsc
    """
    response = await fetch_ave(f"/tokens/{token_id}")
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

@app.get("/klines/pair/{pair_id}", tags=["Charts"])
async def get_pair_kline(
    pair_id: str,
    interval: int = Query(60, description="Time interval in seconds (15,30,60,120,240,1440,4320,10080,43200)"),
    size: int = Query(10, description="Number of records to return"),
    category: str = Query("u", description="Category type (u for USD, b for base token)")
):
    """
    Get k-line (candlestick) data for a trading pair.
    Format: {pair}-{chain}
    """
    response = await fetch_ave(f"/klines/pair/{pair_id}", {
        "interval": interval,
        "size": size,
        "category": category
    })
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

@app.get("/klines/token/{token_id}", tags=["Charts"])
async def get_token_kline(
    token_id: str,
    interval: int = Query(60, description="Time interval in seconds (15,30,60,120,240,1440,4320,10080,43200)"),
    size: int = Query(10, description="Number of records to return")
):
    """
    Get k-line (candlestick) data for a token.
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/klines/token/{token_id}", {
        "interval": interval,
        "size": size
    })
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه بهینه نمودار توکن برای GPT
@app.get("/klines/token/limited/{token_id}", tags=["GPT Optimized"])
async def get_token_kline_limited(
    token_id: str,
    interval: int = Query(1440, description="Time interval in seconds (15,30,60,120,240,1440,4320,10080,43200)"),
    size: int = Query(5, description="Number of records to return (limited for GPT)")
):
    """
    Get limited k-line (candlestick) data for a token (GPT-optimized).
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/klines/token/{token_id}", {
        "interval": interval,
        "size": size
    })
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

@app.get("/tokens/top100/{token_id}", tags=["Token Analytics"])
async def get_top100(token_id: str):
    """
    Get top 100 holders of a specific token.
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/tokens/top100/{token_id}")
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه محدود دارندگان برتر برای GPT
@app.get("/tokens/top/{token_id}", tags=["GPT Optimized"])
async def get_top_holders(
    token_id: str,
    limit: int = Query(10, description="Number of top holders to return")
):
    """
    Get limited number of top holders of a specific token (GPT-optimized).
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/tokens/top100/{token_id}")
    
    # استخراج و محدود کردن داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"][:limit]
    return response

@app.get("/txs/{pair_id}", tags=["Transactions"])
async def get_pair_txs(
    pair_id: str,
    limit: int = Query(10, description="Number of records to return"),
    to_time: Optional[int] = Query(None, description="Timestamp of latest record")
):
    """
    Get transactions for a specific trading pair.
    Format: {pair}-{chain}
    """
    params = {"limit": limit}
    if to_time:
        params["to_time"] = to_time
    
    response = await fetch_ave(f"/txs/{pair_id}", params)
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه محدود تراکنش‌ها برای GPT
@app.get("/txs/limited/{pair_id}", tags=["GPT Optimized"])
async def get_pair_txs_limited(
    pair_id: str,
    limit: int = Query(5, description="Number of records to return (limited for GPT)"),
    to_time: Optional[int] = Query(None, description="Timestamp of latest record")
):
    """
    Get limited transactions for a specific trading pair (GPT-optimized).
    Format: {pair}-{chain}
    """
    params = {"limit": limit}
    if to_time:
        params["to_time"] = to_time
    
    response = await fetch_ave(f"/txs/{pair_id}", params)
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

@app.get("/supported_chains", tags=["Chains"])
async def get_supported_chains():
    """
    Get list of supported blockchains.
    """
    response = await fetch_ave("/supported_chains")
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# دریافت لیست روند زنجیره
@app.get("/chain_trending", tags=["Trending"])
async def get_chain_trending(
    chain_name: str = Query(..., description="Chain name to get trending tokens")
):
    """
    Get trending tokens for a specific blockchain.
    """
    response = await fetch_ave(f"/tokens/trending", {"chain": chain_name})
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# ✨ NEW: نسخه محدود توکن‌های روند دار برای GPT
@app.get("/chain_trending/limited", tags=["GPT Optimized"])
async def get_chain_trending_limited(
    chain_name: str = Query(..., description="Chain name to get trending tokens"),
    limit: int = Query(5, description="Number of trending tokens to return")
):
    """
    Get limited trending tokens for a specific blockchain (GPT-optimized).
    """
    response = await fetch_ave(f"/tokens/trending", {"chain": chain_name})
    
    # استخراج و محدود کردن داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"][:limit]
    return response

# قرارداد ریسک تشخیص گزارش
@app.get("/contracts/{token_id}", tags=["Risk Analysis"])
async def get_contract_risk_detection(token_id: str):
    """
    Get contract risk detection report for a token.
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/contracts/{token_id}")
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# دریافت توکن‌های اصلی زنجیره
@app.get("/tokens/main", tags=["Chains"])
async def get_chain_main_tokens(
    chain_name: str = Query(..., description="Chain name to get main tokens")
):
    """
    Get chain's main token list.
    """
    response = await fetch_ave(f"/tokens/main", {"chain": chain_name})
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

# دریافت قیمت توکن
@app.post("/tokens/price", tags=["Prices"])
async def get_token_prices(
    token_ids: List[str] = Query(..., description="List of token IDs (max 200)")
):
    """
    Get token latest prices.
    Format: Each ID should be {token}-{chain}
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/tokens/price", 
            headers=HEADERS,
            json={"token_ids": token_ids}
        ) as response:
            if response.status >= 400:
                error_msg = await response.text()
                raise HTTPException(status_code=response.status, detail=error_msg)
            
            result = await response.json()
            
            # استخراج داده‌ها از پاسخ
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result

# ✨ NEW: خلاصه جامع توکن برای GPT
@app.get("/token_summary/{token_id}", tags=["GPT Optimized"])
async def get_token_summary(token_id: str):
    """
    Get comprehensive token summary in a single request (GPT-optimized).
    Combines basic info, market data, and top 5 holders.
    Format: {token}-{chain}
    """
    # دریافت اطلاعات اصلی توکن
    token_info_response = await fetch_ave(f"/tokens/{token_id}")
    token_info = {}
    if isinstance(token_info_response, dict) and "data" in token_info_response:
        token_info = token_info_response["data"]
    
    # دریافت گزارش ریسک قرارداد
    contract_risk_response = await fetch_ave(f"/contracts/{token_id}")
    contract_risk = {}
    if isinstance(contract_risk_response, dict) and "data" in contract_risk_response:
        contract_risk = contract_risk_response["data"]
    
    # دریافت ۵ دارنده برتر
    top_holders_response = await fetch_ave(f"/tokens/top100/{token_id}")
    top_holders = []
    if isinstance(top_holders_response, dict) and "data" in top_holders_response:
        top_holders = top_holders_response["data"][:5]  # فقط ۵ دارنده برتر
    
    # ترکیب همه اطلاعات در یک پاسخ
    return {
        "token_info": token_info,
        "risk_analysis": contract_risk,
        "top_holders": top_holders
    }
