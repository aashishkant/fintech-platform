import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# API Keys
ALPHA_VANTAGE_API_KEY = "BE188DMZ5ZONQW45"
METAL_PRICE_API_KEY = "a93c548abe4132543fa1cbbfbf1a9db6"
FINNHUB_API_KEY = "cva46khr01qshflfvm40cva46khr01qshflfvm4g"
FREECURRENCY_API_KEY = "fca_live_qeBX1phtQnQaOIoM5Kh4GKiHQbOdCrldl8kobvdB"

# API URLs
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
METAL_PRICE_URL = "https://api.metalpriceapi.com/v1"
FINNHUB_URL = "https://finnhub.io/api/v1"
FREECURRENCY_URL = "https://api.freecurrencyapi.com/v1/latest"

# Indian Indices
INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY Pharma": "^CNXPHARMA",
    "NIFTY Midcap 100": "^NSEMDCP50",
    "NIFTY Smallcap 100": "^CNXSC",
    "NIFTY Auto": "^CNXAUTO",
    "NIFTY Energy": "^CNXENERGY"
}

# Sector Indices
SECTOR_INDICES = {
    "Banking": "^NSEBANK",
    "IT": "^CNXIT",
    "Pharma": "^CNXPHARMA",
    "Auto": "^CNXAUTO",
    "Energy": "^CNXENERGY",
    "FMCG": "^CNXFMCG",
    "Metal": "^CNXMETAL",
    "Realty": "^CNXREALTY"
}

# Top Indian Stocks
TOP_STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Tata Steel": "TATASTEEL.NS"
}

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_stock_data(symbol: str) -> Dict:
    """Fetch real-time stock data with yfinance as primary source."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        if not hist.empty:
            return {
                "symbol": symbol,
                "price": info.get("regularMarketPrice", hist['Close'].iloc[-1]),
                "change": info.get("regularMarketChange", hist['Close'].iloc[-1] - hist['Open'].iloc[-1]),
                "change_percent": info.get("regularMarketChangePercent", (hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1] * 100),
                "volume": info.get("regularMarketVolume", hist['Volume'].iloc[-1]),
                "last_updated": hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        logger.warning(f"yfinance failed for {symbol}: {e}. Trying Alpha Vantage.")

    try:
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_API_KEY}
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("Global Quote", {})
        if data:
            return {
                "symbol": symbol,
                "price": float(data["05. price"]),
                "change": float(data["09. change"]),
                "change_percent": float(data["10. change percent"].strip('%')),
                "volume": int(data["06. volume"]),
                "last_updated": data["07. latest trading day"]
            }
    except Exception as e:
        logger.error(f"All sources failed for {symbol}: {e}")
        st.error(f"Data unavailable for {symbol}.")
        return {"symbol": symbol, "price": 0, "change": 0, "change_percent": 0, "volume": 0, "last_updated": "N/A"}

@st.cache_data(ttl=300)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_metal_prices() -> Dict:
    """Fetch gold and silver prices in INR."""
    try:
        params = {"api_key": METAL_PRICE_API_KEY, "base": "USD", "currencies": "XAU,XAG,INR"}
        response = requests.get(f"{METAL_PRICE_URL}/latest", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "rates" not in data:
            raise ValueError("Invalid metal price data")
        gold_price_per_ounce = 1 / float(data["rates"]["XAU"])
        silver_price_per_ounce = 1 / float(data["rates"]["XAG"])
        usd_to_inr = float(data["rates"]["INR"])
        timestamp = datetime.fromtimestamp(int(data["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
        return {
            "gold": {"price": round((gold_price_per_ounce * usd_to_inr) / 31.1035, 2), "last_updated": timestamp},
            "silver": {"price": round((silver_price_per_ounce * usd_to_inr) / 31.1035, 2), "last_updated": timestamp}
        }
    except Exception as e:
        logger.error(f"Metal Price API failed: {e}")
        st.error("Metal prices unavailable.")
        return {"gold": {"price": 0, "last_updated": "N/A"}, "silver": {"price": 0, "last_updated": "N/A"}}

@st.cache_data(ttl=3600)
def fetch_historical_data(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Fetch historical data using yfinance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval="1d")
        if df.empty:
            raise ValueError(f"No historical data for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Historical data fetch failed for {symbol}: {e}")
        st.error(f"Cannot fetch historical data for {symbol}.")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_sector_performance() -> Dict:
    """Fetch performance data for sector indices."""
    return {sector: fetch_stock_data(symbol) for sector, symbol in SECTOR_INDICES.items()}

@st.cache_data(ttl=300)
def fetch_top_stocks() -> Dict:
    """Fetch data for top Indian stocks."""
    return {name: fetch_stock_data(symbol) for name, symbol in TOP_STOCKS.items()}

@st.cache_data(ttl=300)
def fetch_currency_rates() -> Dict:
    """Fetch live USD/INR and EUR/INR rates."""
    try:
        params = {"apikey": FREECURRENCY_API_KEY, "base_currency": "USD", "currencies": "INR,EUR"}
        response = requests.get(FREECURRENCY_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
        usd_inr = float(data["INR"])
        eur_usd = float(data["EUR"])
        eur_inr = usd_inr / eur_usd
        return {"USD/INR": usd_inr, "EUR/INR": eur_inr}
    except Exception as e:
        logger.error(f"FreeCurrencyAPI failed: {e}. Falling back to defaults.")
        st.error("Currency data unavailable.")
        return {"USD/INR": 84.0, "EUR/INR": 92.0}

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for financial analysis."""
    if df.empty:
        return df
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Volatility'] = df['Close'].pct_change().rolling(window=20).std() * (252 ** 0.5)
    return df

def get_major_indian_indices() -> List[str]:
    """Return list of major Indian indices symbols."""
    return list(INDICES.values())