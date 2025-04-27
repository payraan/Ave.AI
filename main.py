from fastapi import FastAPI, HTTPException, Query, Depends, Path
import aiohttp
import logging
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Union
from enum import Enum

# تنظیم لاگینگ برای مشاهده خطاهای دقیق
logging.basicConfig(level=logging.DEBUG)

# بارگذاری متغیرهای محیطی
load_dotenv()

# 🔐 کلید API از متغیر محیطی یا مقدار پیش‌فرض
AVE_API_KEY = os.getenv("AVE_API_KEY", "mspSf2Ai4AmgfY6qZ1B3hXEZaiM5o2tvAAA6zc5yB0ptGyxnjz841GBiHAivx8xl")

# تعریف کلاس Enum برای تعداد هولدرها
class HolderLimit(str, Enum):
    top5 = "5"
    top10 = "10"
    top20 = "20"
    top50 = "50"
    top100 = "100"

# تعریف کلاس Enum برای اندازه داده‌های نمودار
class ChartSize(int, Enum):
    small = 5
    medium = 10
    large = 20
    xlarge = 50

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
    chain: Optional[str] = Query(None, description="Blockchain name (optional)"),
    limit: int = Query(10, description="Maximum number of results to return", ge=1, le=50)
):
    """
    Search for tokens by name, symbol or contract address.
    Returns a list of matching tokens with a customizable limit.
    """
    params = {"keyword": keyword}
    if chain:
        params["chain"] = chain
    
    response = await fetch_ave("/tokens", params)
    
    # استخراج داده‌های توکن از پاسخ و محدود کردن نتایج
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
    size: ChartSize = Query(ChartSize.medium, description="Number of records to return"),
    category: str = Query("u", description="Category type (u for USD, b for base token)")
):
    """
    Get k-line (candlestick) data for a trading pair with customizable size.
    Format: {pair}-{chain}
    """
    response = await fetch_ave(f"/klines/pair/{pair_id}", {
        "interval": interval,
        "size": int(size),
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
    size: ChartSize = Query(ChartSize.medium, description="Number of records to return")
):
    """
    Get k-line (candlestick) data for a token with customizable size.
    Format: {token}-{chain}
    """
    response = await fetch_ave(f"/klines/token/{token_id}", {
        "interval": interval,
        "size": int(size)
    })
    
    # استخراج داده‌ها از پاسخ
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response

@app.get("/tokens/holders/{token_id}", tags=["Token Analytics"])
async def get_token_holders(
    token_id: str,
    limit: HolderLimit = Query(HolderLimit.top20, description="Number of top holders to return")
):
    """
    Get top holders of a specific token with customizable limit.
    Format: {token}-{chain}
    Options: 5, 10, 20, 50, or 100 holders
    """
    response = await fetch_ave(f"/tokens/top100/{token_id}")
    
    # استخراج داده‌ها از پاسخ و محدود کردن براساس پارامتر limit
    if isinstance(response, dict) and "data" in response:
        limit_int = int(limit.value)
        return response["data"][:limit_int]
    return response

# جمع‌آوری اطلاعات توکن در یک درخواست
@app.get("/token_info/{token_id}", tags=["Comprehensive"])
async def get_token_info(
    token_id: str,
    holder_limit: HolderLimit = Query(HolderLimit.top5, description="Number of top holders to include"),
    chart_size: ChartSize = Query(ChartSize.small, description="Number of chart points to include"),
    chart_interval: int = Query(1440, description="Chart interval in seconds")
):
    """
    Get comprehensive token information including details, chart data and top holders in a single request.
    All data is limited for optimal processing by AI assistants.
    Format: {token}-{chain}
    """
    # دریافت اطلاعات اصلی توکن
    token_details_response = await fetch_ave(f"/tokens/{token_id}")
    token_details = {}
    if isinstance(token_details_response, dict) and "data" in token_details_response:
        token_details = token_details_response["data"]
    
    # دریافت داده‌های نمودار
    chart_response = await fetch_ave(f"/klines/token/{token_id}", {
        "interval": chart_interval,
        "size": int(chart_size)
    })
    chart_data = {}
    if isinstance(chart_response, dict) and "data" in chart_response:
        chart_data = chart_response["data"]
    
    # دریافت دارندگان برتر
    holders_response = await fetch_ave(f"/tokens/top100/{token_id}")
    holders = []
    if isinstance(holders_response, dict) and "data" in holders_response:
        limit_int = int(holder_limit.value)
        holders = holders_response["data"][:limit_int]
    
    # ترکیب همه اطلاعات در یک پاسخ
    return {
        "token_details": token_details,
        "chart_data": chart_data,
        "top_holders": holders
    }
