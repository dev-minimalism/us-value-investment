[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![yfinance](https://img.shields.io/badge/yfinance-410093)](https://pypi.org/project/yfinance/)
[![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?logo=googlesheets&logoColor=white)](https://developers.google.com/sheets/api)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)

# 가상환경 구성
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# requirements.txt 만드려면
```
pip freeze > requirements.txt
```


# mac, linux에서 crontab 실행하려면
```
crontab -e
0 11 * * * ~/code/value-investment/venv/bin/python ~/code/value-investment/main.py
```

### Test Google Sheets mode:
```
nohup python main.py --mode sheets > output_file/logs/nohup.out 2>&1 &
```
### Test monitoring mode:
```
nohup python main.py --mode monitor > output_file/logs/nohup.out 2>&1 &
```
