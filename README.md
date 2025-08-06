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
