# --- 내재가치 계산 ---
from config.config import TARGET_PE


def estimate_intrinsic_value(eps):
  return eps * TARGET_PE if eps and eps > 0 else None
