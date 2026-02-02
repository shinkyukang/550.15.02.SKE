AI모델 예측값 : AI모델 예측에 사용된 중요 변수 파일 (png 파일 5개는 원유 보고서 Appendix에 추가)
daily_predictions.csv : 예측값의 결과 파일이며, 예측값의 상위 5개를 사용 (12.05 기준 12.08 ~ 12.12 예측값을 평균)
기초 자료 작성 폴더: AA-OIL-BRENT.csv(브렌트유 가격 파일), recent_x_data.csv(모델에서 사용하는 최근 1달 변수 파일),
full_stages_log.json(위에 2개 파일로 LLM 기반 분석 자료 작성 - 상승/하락에 대한 논리)
oil_market_lexicon_v3.json : 보고서 템플릿, 양식, 표현 등을 정의한 사전 파일
원유 Report 프롬프트: 2단계에 걸쳐서 파일을 보고서를 작성함(chatgpt 5.1 Thinking 활용)
1. 위에 full_stages_log.json 파일, 분석 자료를 기반으로 전망 보고서에 사용할 기초 자료를 작성
2. 기초 자료를 기반으로 전망보고서를 작성
위에 전망보고서 내용으로 "Brent 원유 전망.pdf" 파일을 작성하는데 Typora로 보고서 형태로 만들고 pdf로 export 함
