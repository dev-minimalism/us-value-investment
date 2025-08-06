# --- 시그널 생성 로직 ---
from config.config import ROE_THRESHOLD, DE_THRESHOLD, VALUATION_MULTIPLIER, \
  SELL_MULTIPLIER
from valuation.valuation import estimate_intrinsic_value


def evaluate_stock(data):
  eps = data.get('eps')
  intrinsic = estimate_intrinsic_value(eps)
  if intrinsic is None:
    return None
  price = data['price']
  roe = data.get('roe')
  de = data.get('de_ratio')
  if roe is None or de is None or roe < ROE_THRESHOLD or de > DE_THRESHOLD:
    return None
  if price < intrinsic * VALUATION_MULTIPLIER:
    return 'BUY'
  elif price > intrinsic * SELL_MULTIPLIER:
    return 'SELL'
  else:
    return 'HOLD'
