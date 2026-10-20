# US Value Investment

[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![yfinance](https://img.shields.io/badge/yfinance-410093)](https://pypi.org/project/yfinance/)
[![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?logo=googlesheets&logoColor=white)](https://developers.google.com/sheets/api)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

S&P 500 시가총액 상위 200개 종목을 가치투자 기준으로 평가해 매수/매도/보유 시그널을 생성하고,
결과를 Google Sheets에 업로드하며 Telegram으로 알림을 보내는 스크립트입니다.

## 동작 방식

1. 위키피디아에서 S&P 500 종목 목록을 가져와 yfinance 시가총액 기준 상위 200개를 선정
2. 각 종목의 주가, EPS, P/E, P/B, ROE, 부채비율(D/E)을 yfinance로 수집
3. 시그널 판단 (기준값은 `config/config.py`에서 조정)
   - 내재가치 = EPS × 15 (`TARGET_PE`), EPS가 0 이하이거나 없으면 판단 제외
   - ROE < 10% 또는 D/E > 1.0배인 종목은 판단 제외
   - **BUY**: 주가 < 내재가치 × 0.75
   - **SELL**: 주가 > 내재가치 × 1.2
   - **HOLD**: 그 사이
4. 결과를 `output_file/today_signals_<시각>.xlsx`로 저장 (BUY는 빨강, SELL은 파랑)

## 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

의존성을 갱신했다면 `pip freeze > requirements.txt`로 다시 생성합니다.

## 설정

### 환경 변수

| 변수 | 설명 |
| --- | --- |
| `US_VALUE_INVESTMENT_TELEGRAM_BOT_TOKEN` | Telegram 봇 토큰 |
| `US_VALUE_INVESTMENT_TELEGRAM_CHAT_ID` | 알림을 받을 채팅 ID |
| `GDRIVE_FOLDER_ID` | 업로드할 Google Drive 폴더 ID (생략 시 내 드라이브 루트) |

### Google Drive 인증

1. Google Cloud Console에서 OAuth 클라이언트(데스크톱 앱)를 만들고 `secret/client_secret.json`으로 저장
2. 첫 실행 시 브라우저에서 동의하면 `secret/token.pickle`에 토큰이 저장되어 이후에는 자동 인증

`secret/`과 `output_file/`은 git에 포함되지 않습니다.

## 실행

```bash
# 평가 실행 → 엑셀 저장 → Google Sheets 업로드 (1회)
python main.py --mode sheets

# 최신 결과 파일을 감시하며 BUY/SELL 종목을 Telegram으로 알림 (상시 실행)
python main.py --mode monitor
```

모니터 모드는 1분마다 `output_file/`의 최신 결과 파일을 확인하고, 미국 장 시간(KST 22:30–05:00)에
파일이 갱신되면 알림을 보냅니다. 장 시간 중에는 2시간마다 동작 확인(heartbeat) 메시지도 보냅니다.

### 백그라운드 실행

```bash
mkdir -p output_file/logs
nohup python main.py --mode sheets  > output_file/logs/nohup.out 2>&1 &
nohup python main.py --mode monitor > output_file/logs/nohup.out 2>&1 &
```

### crontab으로 매일 실행 (mac, linux)

```bash
crontab -e
```

```
0 11 * * * cd ~/code/value-investment && venv/bin/python main.py --mode sheets
```

`--mode`는 필수 인자이며, 일부 파일이 현재 작업 디렉터리 기준으로 저장되므로 `cd`로 프로젝트 폴더에서 실행해야 합니다.

## 프로젝트 구조

```
main.py          # 진입점: 실행 모드, 엑셀 저장, Telegram 알림
config/          # 시그널 판단 기준값
fetch_data/      # 종목 목록 및 재무 데이터 수집 (Wikipedia, yfinance)
valuation/       # 내재가치 계산
signaler/        # BUY/SELL/HOLD 판단
google_sheet/    # Google Drive 업로드 및 Sheets 변환
```

## 면책 조항

이 프로젝트는 학습 및 개인 연구 목적으로 작성되었으며, 투자 권유나 금융 자문이 아닙니다.
생성되는 BUY/SELL/HOLD 시그널은 단순한 재무 지표 기준에 따른 참고 정보일 뿐이며,
데이터의 정확성이나 수익을 보장하지 않습니다. 모든 투자 판단과 그 결과에 대한 책임은 사용자 본인에게 있습니다.

## 라이선스

[MIT](LICENSE)
