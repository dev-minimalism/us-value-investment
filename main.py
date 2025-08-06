import os
from datetime import datetime

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill

from fetch_data.fetch_data import get_sp500_top200_tickers, get_financial_data
from google_sheet.google_sheet import upload_and_convert_to_gsheet
from signaler.signaler import evaluate_stock


def signal_description(signal):
  return {
    'BUY': '저평가 - 매수 고려',
    'SELL': '고평가 - 매도 고려',
    'HOLD': '적정가 - 보유 유지'
  }.get(signal, '의견 없음')  # 기본값 지정


def save_colored_excel(df, filename='signals.xlsx'):
  wb = Workbook()
  ws = wb.active

  # 헤더
  ws.append(df.columns.tolist())

  # 색상 정의
  red_fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC",
                         fill_type="solid")  # BUY
  blue_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF",
                          fill_type="solid")  # SELL

  # 데이터 행 추가 및 색상 적용
  for i, row in df.iterrows():
    row_data = row.tolist()
    ws.append(row_data)

    # 색상 적용
    decision = row.get('decision', '')
    target_cell = ws.cell(row=i + 2, column=df.columns.get_loc(
        'decision') + 1)  # +2 for header and 1-based index

    if decision == 'BUY':
      target_cell.fill = red_fill
    elif decision == 'SELL':
      target_cell.fill = blue_fill

  wb.save(filename)
  print(f"🎨 색상 포함된 파일 저장 완료: {filename}")


# --- 전체 파이프라인 실행 ---
def run_pipeline():
  results = []
  TICKERS = get_sp500_top200_tickers()

  for ticker in TICKERS:
    data = get_financial_data(ticker)
    if not data:
      continue

    signal = evaluate_stock(data)
    data['decision'] = signal if signal else '없음'
    data['comment'] = signal_description(signal)
    results.append(data)

  df = pd.DataFrame(results)

  df = df[['ticker', 'price', 'eps', 'pe', 'pb', 'roe', 'de_ratio', 'decision',
           'comment']]

  # ✅ 디렉토리 생성
  # 현재 파일이 위치한 디렉토리 기준으로 절대 경로 생성
  base_dir = os.path.dirname(os.path.abspath(__file__))

  # 출력 디렉토리 설정
  output_dir = os.path.join(base_dir, 'output_file')
  os.makedirs(output_dir, exist_ok=True)

  # 날짜 포함된 파일명 생성
  today = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
  filename = os.path.join(output_dir, f'today_signals_{today}.xlsx')

  save_colored_excel(df, filename)
  print(f"✅ 평가 결과 저장 완료 → {filename}")

  gdrive_folder_id = '198E9_yTSeQCjeJXwJFDgnmiZAtCNCJMC'  # ← 여기에 본인 폴더 ID 넣기
  upload_and_convert_to_gsheet(filename, gdrive_folder_id)


# --- 실행 ---
if __name__ == "__main__":
  run_pipeline()
