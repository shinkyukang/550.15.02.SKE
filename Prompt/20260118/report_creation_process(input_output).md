# 유가 전망 보고서 생성 프로세스

## 개요
브렌트유 가격 예측 AI 모델 기반 전망 리포트 생성을 위한 3단계 프로세스

---

## Stage 0: 데이터 수집 및 모델 실행

    ### Process
    ```
    /Code/oil_forecast_report/
    ```

    ### Input
    | 파일명              | 설명                 |
    | ------------------- | -------------------- |
    | `AA-OIL_BRENT.csv`  | 브렌트유 가격 데이터 |
    | `recent_x_data.csv` | 최근 설명변수 데이터 |

    ### Output
    ```
    full_states_log_YYYY-MM-DD.json
    ```

---

## Stage 1: 1차 분석 (시나리오 생성)

    ### Process
    ChatGPT 5.2 (Web Browser)

    ### Input

    #### 1. 프롬프트 파일
    - `report_creation_Prompt_stage1_260126.md`

    #### 2. 변수 설정 지침
    | 변수               | 값                              | 데이터 소스             |
    | ------------------ | ------------------------------- | ----------------------- |
    | `{MAIN_SCENARIO}`  | `increase` 또는 `decrease`      | 아래 조건에 따라 결정   |
    | `{BASE_PRICE}`     | 마지막 실적 종가 (y_base)       | `daily_predictions.csv` |
    | `{FORECAST_PRICE}` | 최근 5일 예측 평균 (prediction) | `daily_predictions.csv` |

    #### 3. MAIN_SCENARIO 결정 기준
    - 최근 5일 예측 평균(`prediction`)과 마지막 실적 종가(`y_base`)의 차이를 기준으로 판단
    - 예측 평균 > 실적 종가 → `increase`
    - 예측 평균 < 실적 종가 → `decrease`

    #### 4. MarketAgentsStrategy_logs
    - `full_states_log_YYYY-MM-DD.json`

    ### Output
    ```
    stage1_result_YYMMDD.md
    ```

---

## Stage 2: 2차 분석 (최종 보고서 생성)

    ### Process
    ChatGPT 5.2 (Web Browser)

    ### Input

    #### 1. 프롬프트 파일
    - `report_creation_Prompt_stage2_260126.md`

    #### 2. 변수 설정 지침
    | 변수               | 값                      | 비고                           |
    | ------------------ | ----------------------- | ------------------------------ |
    | `{MAIN_SCENARIO}`  | Stage 1과 동일          | `increase` 또는 `decrease`     |
    | `{DATE_RANGE}`     | Stage 1 결과에서 가져옴 | `stage1_result_YYMMDD.md` 참조 |
    | `{BASE_PRICE}`     | Stage 1 결과에서 가져옴 | `stage1_result_YYMMDD.md` 참조 |
    | `{FORECAST_PRICE}` | Stage 1 결과에서 가져옴 | `stage1_result_YYMMDD.md` 참조 |

    #### 3. 참조 파일
    - `stage1_result_YYMMDD.md` (Stage 1 결과)
    - `oil_market_lexicon_v3.json` (유가 시장 용어 사전)

    ### Output
    ```
    SKT_유가전망_AI모델_전망리포트_브렌트유_260126.md
    ```
    > **Note:** Appendix 2, 3, 4는 별도 첨부 (without appendix 2, 3, 4)

---

## 부록 (Appendix) 소스

| 부록       | 소스 파일                                                            |
| ---------- | -------------------------------------------------------------------- |
| Appendix 1 | `stage1_result_YYMMDD.md`의 [1-A] 섹션                               |
| Appendix 2 | `impact_category_monthly.png`                                        |
| Appendix 3 | `impact_week_top_variable_A.png`, `impact_week_top_variable_B.png`   |
| Appendix 4 | `impact_month_top_variable_A.png`, `impact_month_top_variable_B.png` |

---

## 플로우차트

```
[Stage 0]                    [Stage 1]                    [Stage 2]
    │                            │                            │
    ▼                            ▼                            ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│ 모델 실행    │            │ 1차 분석     │            │ 최종 보고서  │
│             │            │             │            │             │
│ Input:      │            │ Input:      │            │ Input:      │
│ - 유가 데이터 │───────────▶│ - 프롬프트   │───────────▶│ - 프롬프트   │
│ - 설명변수   │            │ - 예측 결과  │            │ - Stage1 결과│
│             │            │             │            │ - 용어 사전  │
│ Output:     │            │ Output:     │            │             │
│ full_states │            │ stage1_     │            │ Output:     │
│ _log.json   │            │ result.md   │            │ 최종 리포트  │
└─────────────┘            └─────────────┘            └─────────────┘
```
