import json
import sys
import os

# 커맨드 라인 인자로 파일명 받기
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    # 인자가 없으면 사용자에게 입력 요청
    print('JSON 파일명을 입력하세요 (예: full_states_log_2026-01-26.json)')
    input_file = input('파일명: ').strip()

# 파일 존재 여부 확인
if not os.path.exists(input_file):
    print(f'오류: "{input_file}" 파일을 찾을 수 없습니다.')
    sys.exit(1)

# 출력 파일명 자동 생성
output_file = input_file.replace('.json', '.md')

print(f'JSON 파일 읽는 중: {input_file}')

# JSON 파일 읽고 파싱
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('JSON 파싱 완료!')
print('마크다운 변환 중...')

# 데이터 추출 (JSON 파일의 첫 번째 날짜 키를 자동으로 찾음)
date_key = list(data.keys())[0]
print(f'찾은 날짜: {date_key}')
report = data[date_key]

# 마크다운 생성
markdown = f"""# Brent Crude Oil Complete Analysis Report

**Trade Date:** {report['trade_date']}

**Company of Interest:** {report['company_of_interest']}

---

## 1️⃣ Market Report (Daily Chart Assessment)

{report['market_report']}

---

## 2️⃣ Sentiment Report

{report['sentiment_report']}

---

## 3️⃣ News Report

{report['news_report']}

---

## 4️⃣ Fundamentals Report

{report['fundamentals_report']}

---

## 5️⃣ Investment Plan

{report['investment_plan']}

---

## 6️⃣ Final Trade Decision

{report['final_trade_decision']}

---

## 📈 Bull Case Analysis

{report['investment_debate_state']['bull_history']}

---

## 📉 Bear Case Analysis

{report['investment_debate_state']['bear_history']}

---

## 🔥 Risky Analyst View

{report['risk_debate_state']['risky_history']}

---

## 🛡️ Safe Analyst View

{report['risk_debate_state']['safe_history']}

---

## ⚖️ Neutral Analyst View

{report['risk_debate_state']['neutral_history']}
"""

# 파일로 저장
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(markdown)

print('✅ 변환 완료!')
print(f'📄 생성된 파일: {output_file}')
print()
print('🎉 다음 단계:')
print(f'1. VS Code에서 "{output_file}" 파일 열기')
print('2. Ctrl + Shift + V 눌러서 마크다운 미리보기 보기')