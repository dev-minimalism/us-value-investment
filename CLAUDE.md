# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A script that screens S&P 500 stocks for value-investing signals (BUY/SELL/HOLD), writes the results to a color-coded Excel file, uploads it to Google Drive as a Google Sheet, and sends Telegram alerts. User-facing strings and comments are mostly in Korean.

## Commands

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python main.py --mode sheets    # run the full pipeline once: screen → xlsx → upload to Google Sheets
python main.py --mode monitor   # long-running loop that watches output_file/ and sends Telegram alerts
```

The README runs both modes under `nohup` (logs go to `output_file/logs/nohup.out`), and runs `sheets` mode daily from crontab. There are no tests, no linter config, and no build step.

Required env vars: `US_VALUE_INVESTMENT_TELEGRAM_BOT_TOKEN`, `US_VALUE_INVESTMENT_TELEGRAM_CHAT_ID`, `GDRIVE_FOLDER_ID` (optional; if unset, the file is uploaded to the Drive root).

Google OAuth reads `secret/client_secret.json` and caches credentials in `secret/token.pickle`. The first run opens a browser for consent. `secret/` and `output_file/` are gitignored.

## Architecture

The two modes are separate processes. They communicate only through files on disk:

1. **`sheets` mode** (`main.run_pipeline`):
   - `fetch_data.get_sp500_top200_tickers()` scrapes the S&P 500 list from Wikipedia, gets each ticker's `marketCap` from yfinance (about 500 slow `.info` calls), and keeps the top 200.
   - For each of those tickers, `get_financial_data()` pulls price, EPS, P/E, P/B, ROE and D/E from `yf.Ticker(t).info`.
   - `signaler.evaluate_stock()` decides the signal and `save_colored_excel()` writes `output_file/today_signals_<timestamp>.xlsx`, filling BUY cells red and SELL cells blue.
   - `google_sheet.upload_and_convert_to_gsheet()` uploads that file with the Google Sheets mimeType, so Drive converts it.
2. **`monitor` mode** (`main.monitor_and_notify`) polls every 60s for the newest `today_signals_*.xlsx` by mtime. When the file changes during US market hours, it sends one Telegram message per BUY/SELL row. During market hours it also sends a heartbeat every 2h. `last_modified` starts at 0, so at startup it re-sends alerts for the current latest file.

**Signal logic** (`signaler` → `valuation`, thresholds in `config/config.py`):
- Intrinsic value = `EPS × TARGET_PE` (15). If EPS ≤ 0 or is missing, there is no signal.
- Filter: a stock gets no signal if ROE < `ROE_THRESHOLD` or D/E > `DE_THRESHOLD`.
- BUY if price < intrinsic × 0.75. SELL if price > intrinsic × 1.2. Anything in between is HOLD.
- A `None` signal becomes `'없음'` in the `decision` column.

## Gotchas

- yfinance's `debtToEquity` is a percentage (e.g. `150` means 1.5×). `get_financial_data()` divides it by 100, so `de_ratio` (in the Excel output too) and `DE_THRESHOLD` are both plain ratios.
- `fetch_data` writes `sp500_top200_by_marketcap.csv` to `./output_file`, relative to the **working directory**. `main.py` resolves `output_file` relative to the **script directory**. These two paths differ when the script runs from another cwd, as it does under cron.
- `is_us_market_open()` hard-codes 22:30–05:00 KST, which does not adjust for US daylight saving time.
- `.gitignore` does not cover `__pycache__/`, and some `.pyc` files are already committed.
- Code style: 2-space indentation, and absolute package imports from the repo root (e.g. `from config.config import ...`). Run scripts from the repo root.
