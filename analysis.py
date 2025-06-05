import yfinance as yf
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from groq import Groq


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def get_stock_data(ticker: str, period="6mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
    except Exception:
        hist, info = get_from_alpha_vantage(ticker)
    return hist, info
def get_from_alpha_vantage(ticker: str):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_KEY,
        "outputsize": "compact"
    }
    r = requests.get(url, params=params).json()
    ts = r.get("Time Series (Daily)", {})
    df = pd.DataFrame.from_dict(ts, orient="index").sort_index()
    df = df.rename(columns={"5. adjusted close": "Close"})
    df["Close"] = df["Close"].astype(float)
    df.index = pd.to_datetime(df.index)
    return df.tail(120), {"shortName": ticker, "sector": "N/A", "marketCap": "N/A", "longBusinessSummary": "N/A"}

def calculate_indicators(df):
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['Volume'] = df.get('Volume', pd.Series(0))

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    return df



def get_real_time_sentiment(ticker: str) -> str:
    prompt = f"Search the latest 3 news about {ticker}. Summarize sentiment and cite headlines."

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=700,
            top_p=1,
            stream=False
        )

        return completion.choices[0].message.content

    except Exception as e:
        print("Error in sentiment generation:", e)
        return "Sentiment data not available."

def analyze_stock(ticker: str, period="6mo"):
    hist, info = get_stock_data(ticker, period)
    hist = calculate_indicators(hist)
    sentiment = get_real_time_sentiment(ticker)
    return hist, info, sentiment
