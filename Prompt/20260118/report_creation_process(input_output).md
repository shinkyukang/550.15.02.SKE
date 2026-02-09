# 유가 전망 보고서 생성 프로세스

## 개요
브렌트유 가격 예측 AI 모델 기반 전망 리포트 생성을 위한 3단계 프로세스

---

## 경로 정의 (Base Paths)

| 변수           | 경로                                                                                     |
| -------------- | ---------------------------------------------------------------------------------------- |
| `{ROOT}`       | `/Users/shinkyu/Downloads/SKCC/550. AI Agent/550.15.Model_Explainability_Report/550.15.02.SKE` |
| `{CODE}`       | `{ROOT}/Code/oil_forecast_report`                                                        |
| `{PROMPT}`     | `{ROOT}/Prompt/20260118`                                                                 |
| `{INPUT_MODEL}` | `{ROOT}/input_data/Model/20260109`                                                      |
| `{INPUT_PROMPT}` | `{ROOT}/input_data/Prompt/20260109`                                                    |
| `{EVAL_RESULTS}` | `{CODE}/eval_results/Brent crude oil price/MarketAgentsStrategy_logs`                  |

---

## Stage 0: 데이터 수집 및 모델 실행

    ### Process
    ```
    python {CODE}/main.py
    ```
    - 호출: `MarketAgentsGraph.propagate(company_name, target_date)`

    ### Parameters
    | 파라미터         | 값                       |
    | ---------------- | ------------------------ |
    | `company_name`   | `Brent crude oil price`  |
    | `target_date`    | `YYYY-MM-DD`             |

    ### Config (`{CODE}/marketagents/default_config.py`)
    | 설정                       | 값         | 비고                                                                      |
    | -------------------------- | ---------- | ------------------------------------------------------------------------- |
    | `llm_provider`             | `openai`   |                                                                           |
    | `deep_think_llm`           | `o3`       | Market Analyst, Fundamentals Analyst, Research Manager, Risk Manager       |
    | `quick_think_llm`          | `gpt-4.1`  | News Analyst, Social Media Analyst, Bull/Bear Researchers, Trader, Risk Debaters |
    | `max_debate_rounds`        | `2`        | Bull/Bear 토론 횟수                                                       |
    | `max_risk_discuss_rounds`  | `1`        | 리스크 토론 횟수                                                          |
    | `max_recur_limit`          | `100`      |                                                                           |
    | `online_tools`             | `true`     | 실시간 데이터 수집 여부                                                   |

    ### Input
    | 파일명              | 설명                                            |
    | ------------------- | ----------------------------------------------- |
    | `AA-OIL_BRENT.csv`  | 브렌트유 가격 데이터 (최근 250일 사용)           |
    | `recent_x_data.csv` | 200+ 설명변수 데이터 (전체 행 사용)              |

    > **Note:** 두 CSV 파일 모두 target_date까지의 데이터를 포함해야 함

    ### Output
    ```
    full_states_log_YYYY-MM-DD.json
    ```

---

## Stage 1: 1차 분석 (시나리오 생성)

    ### Process
    manual prompt input via chatgpt.com (GPT-5.2)

    ### Input

    #### 1. 프롬프트 파일
    - `report_creation_Prompt_stage1_2026-01-26.md`

    #### 2. 변수 설정 지침
    | 변수               | 값                              | 데이터 소스             |
    | ------------------ | ------------------------------- | ----------------------- |
    | `{MAIN_SCENARIO}`  | `increase` 또는 `decrease`      | 아래 조건에 따라 결정   |
    | `{BASE_PRICE}`     | 마지막 실적 종가 (y_base)       | `daily_predictions.csv` |
    | `{FORECAST_PRICE}` | 최근 5일 예측 평균 (prediction) | `daily_predictions.csv` |

    #### 3. MAIN_SCENARIO 결정 기준
    `{MAIN_SCENARIO}` = 'increase' if FORECAST_PRICE > BASE_PRICE, else 'decrease'

    #### 4. 참조 파일
    - `daily_predictions.csv`
    - `full_states_log_YYYY-MM-DD.json` (copied from stage_0 output)

    ### Output
    ```
    stage1_result_YYYY-MM-DD.md
    ```

---

## Stage 2: 2차 분석 (최종 보고서 생성)

    ### Process
    manual prompt input via chatgpt.com (GPT-5.2)

    ### Input

    #### 1. 프롬프트 파일
    - `report_creation_Prompt_stage2_2026-01-26.md`

    #### 2. 변수 설정 지침
    | 변수               | 값                                            | 비고                               |
    | ------------------ | --------------------------------------------- | ---------------------------------- |
    | `{MAIN_SCENARIO}`  | stage_1과 동일 ('increase' or 'decrease')      | stage_1 instruction에 의해 결정    |
    | `{DATE_RANGE}`     | Stage 1 결과에서 가져옴                        | `stage1_result_YYYY-MM-DD.md` 참조 |
    | `{BASE_PRICE}`     | Stage 1 결과에서 가져옴                        | `stage1_result_YYYY-MM-DD.md` 참조 |
    | `{FORECAST_PRICE}` | Stage 1 결과에서 가져옴                        | `stage1_result_YYYY-MM-DD.md` 참조 |

    #### 3. 참조 파일
    - `stage1_result_YYYY-MM-DD.md` (Stage 1 결과)
    - `oil_market_lexicon_v3.json` (유가 시장 용어 사전)

    ### Output
    ```
    SKT_유가전망_AI모델_전망리포트_브렌트유_2026-01-26.md
    ```
    > **Note:** Appendix 2, 3, 4는 별도 첨부 (without appendix 2, 3, 4)

---

## 부록 (Appendix) 소스

| 부록       | 소스 파일                                                            |
| ---------- | -------------------------------------------------------------------- |
| Appendix 1 | `stage1_result_YYYY-MM-DD.md`의 [1-A] 섹션                          |
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
