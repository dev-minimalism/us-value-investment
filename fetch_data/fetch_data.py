import os
from io import StringIO

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup


# --- 종목 목록 (예: 일부 S&P500) ---
# TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
def get_sp500_top200_tickers():
  print("📥 위키피디아에서 S&P 500 리스트 가져오는 중...")
  url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  table = soup.find('table', {'id': 'constituents'})
  df = pd.read_html(StringIO(str(table)))[0]

  tickers = df['Symbol'].tolist()
  tickers = [t.replace('.', '-') for t in tickers]  # BRK.B → BRK-B

  print("💰 시가총액 데이터 수집 중...")
  ticker_obj = yf.Tickers(tickers)  # ✅ 수정된 부분

  market_caps = {}
  for sym in tickers:
    try:
      market_cap = ticker_obj.tickers[sym].info.get('marketCap', 0)
    except Exception:
      market_cap = 0
    market_caps[sym] = market_cap

  df['MarketCap'] = df['Symbol'].apply(
      lambda x: market_caps.get(x.replace('.', '-'), 0))
  df_sorted = df.sort_values(by='MarketCap', ascending=False)
  top200 = df_sorted.head(200)['Symbol'].tolist()
  top200 = [t.replace('.', '-') for t in top200]

  # 저장할 경로
  output_dir = "./output_file"
  output_path = os.path.join(output_dir, "sp500_top200_by_marketcap.csv")

  # 디렉터리 없으면 생성
  os.makedirs(output_dir, exist_ok=True)
  df_sorted.head(200).to_csv(output_path, index=False)
  print("✅ 상위 200개 시총 리스트 'sp500_top200_by_marketcap.csv' 저장 완료")
  return top200


# --- 데이터 수집 ---
def get_financial_data(ticker):
  stock = yf.Ticker(ticker)
  info = stock.info
  # yfinance는 debtToEquity를 퍼센트로 반환 (예: 150 → 1.5배) → 비율로 변환
  de_pct = info.get('debtToEquity')
  try:
    return {
      'ticker': ticker,
      'price': info['currentPrice'],
      'eps': info.get('trailingEps'),
      'pe': info.get('trailingPE'),
      'pb': info.get('priceToBook'),
      'roe': info.get('returnOnEquity'),
      'de_ratio': de_pct / 100 if de_pct is not None else None,
    }
  except:
    return None
