# HANDOFF — 유가 전망 보고서 파이프라인 리뷰 작업 인수인계

> 작성일: 2026-02-09
> 목적: 다음 에이전트가 이 파일만 읽고 작업을 이어갈 수 있도록 정리

---

## 프로젝트 구조

```
{ROOT} = /Users/shinkyu/Downloads/SKCC/550. AI Agent/550.15.Model_Explainability_Report/550.15.02.SKE
├── Code/oil_forecast_report/          ← Stage 0 코드베이스
│   ├── main.py
│   ├── marketagents/
│   │   ├── agents/
│   │   │   ├── analysts/              ← 4개 분석가 에이전트
│   │   │   ├── managers/              ← research_manager, risk_manager
│   │   │   ├── researchers/           ← bull_researcher, bear_researcher
│   │   │   ├── risk_mgmt/            ← 3개 리스크 토론 에이전트
│   │   │   └── trader/
│   │   ├── graph/                     ← LangGraph 워크플로우 + 프롬프트 템플릿
│   │   └── default_config.py
│   └── eval_results/
├── Prompt/20260118/                   ← Stage 1, 2 프롬프트 및 프로세스 문서
│   ├── report_creation_Prompt_stage1_2026-01-26.md
│   ├── report_creation_Prompt_stage2_2026-01-26.md
│   ├── report_creation_process(input_output).yaml
│   ├── report_creation_process(input_output).md
│   └── oil_market_lexicon_v3.json
└── input_data/                        ← 모델 입력/프롬프트 입력 데이터
```

3단계 파이프라인: Stage 0 (Python 멀티에이전트 실행) → Stage 1 (ChatGPT 프롬프트) → Stage 2 (ChatGPT 프롬프트) → 최종 리포트

---

## 작업 범위

사용자의 요청: 파이프라인 전체(프롬프트 + 코드)에서 **표현이 정확하지 않거나 혼란을 줄 수 있는 부분**을 식별하고 수정

---

## 완료된 작업

### 1. 관측 범위 용어 통일: "30일/30 days" → "1개월/1 month"

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `Code/.../analysts/news_analyst.py` | line 21, 24, 26 | "recent 30 days" → "recent 1 month" (3곳) |
| `Code/.../analysts/social_media_analyst.py` | line 51 | "most recent 30 days" → "recent 1 month period" |
| `Prompt/.../report_creation_Prompt_stage1_2026-01-26.md` | 5곳 | "최근 30일" → "최근 1개월", "30일 전" → "1개월 전" |

### 2. Stage 2 프롬프트 수정 (5건)

| # | 내용 | 상세 |
|---|------|------|
| 1 | 미정의 변수 수정 | `{scenario_label}` → `{MAIN_SCENARIO}`, `{scenario_label_counter}` → `{COUNTER_SCENARIO}` |
| 2 | 섹션 번호 중복 제거 | 제목/부제 앞 "1." 제거 |
| 3 | BASE_PRICE 레이블 수정 | "(내부 AI)" → "(시장 데이터)" |
| 4 | 물결표 수정 | "2-1~~2-3" → "2-1~2-3" (이중 물결표 → 단일) |
| 5 | 단위 명확화 | "10장이내" → "10페이지 이내" |

### 3. Stage 1 프롬프트 수정 (3건, 사용자가 2건 보류)

| # | 내용 | 상태 |
|---|------|------|
| 1 | MAIN_LABEL_EN, COUNTER_HISTORY 미사용 변수 | **보류** (사용자: "일단 변경하지 말아줘") |
| 2 | DATE_RANGE 적용 범위가 news_report에만 한정 | **보류** (사용자: "일단 변경하지 말아줘") |
| 3 | 처리 규칙 2)와 추가 증거 수집 사이 불필요한 구분선 제거 | 완료 |
| 4 | Heading 계층 정리 (##### → ######) | 완료 (총 13곳, 2차 검증에서 2곳 추가 발견하여 수정) |
| 5 | 표 내 날짜 형식 통일 | "9월 22일→ 9월26일" → "9.22 → 9.26" |

### 4. Heading 구조 검증

- **Stage 1**: 수정 완료 (섹션 = `#####`, 하위 항목 = `######`)
- **Stage 2**: 검증 완료 — 이미 올바른 구조. `[10] OUTPUT RULE`에 **bold** 누락 1건은 사용자가 직접 수정

### 5. 코드베이스(Stage 0) 리뷰 — 오타/철자 수정 (4건)

| # | 파일 | 변경 내용 |
|---|------|----------|
| 1 | `Code/.../analysts/news_analyst.py:28` | `Makrdown` → `Markdown` |
| 2 | `Code/.../risk_mgmt/aggresive_debator.py:31` | `halluncinate` → `hallucinate` |
| 3 | `Code/.../risk_mgmt/conservative_debator.py:32` | `halluncinate` → `hallucinate` |
| 4 | `Code/.../risk_mgmt/neutral_debator.py:31` | `halluncinate` → `hallucinate` |

### 6. 코드베이스(Stage 0) 리뷰 — risk_manager.py 버그 수정

**파일:** `Code/oil_forecast_report/marketagents/agents/managers/risk_manager.py:14`

- `fundamentals_report = state["news_report"]` → `state["fundamentals_report"]` 로 수정 완료
- Risk Manager가 news_report를 중복 참조하고 fundamentals_report를 누락하던 버그였음
- 사용자가 직접 수정 (에이전트 식별 → 사용자 수정)

---

## 미완료 / 보류 사항

### [LOW] 파일명 철자 오류

`aggresive_debator.py` → `aggressive_debator.py`

파일명 수정 시 연쇄 변경 필요한 파일 3곳:
- `Code/.../agents/__init__.py:13` — import문
- `Code/oil_forecast_report/CLAUDE.md:51` — 문서 참조
- `Code/oil_forecast_report/CODEBASE_ANALYSIS.md:39` — 문서 참조

**사용자 지시: "파일명은 수정하지 말고"** → 보류

### [INFO] 참고 사항 (수정 불요로 판단)

- `main.py:15` — `target_date = "2025-12-05"` 하드코딩: 매 실행 전 수동 업데이트 값
- risk_mgmt 함수명(`create_risky_debator`) vs 프롬프트 역할명("Risky Risk Analyst") 불일치: 내부 코드 네이밍이므로 동작 영향 없음
- `gpt-4.1` 모델명: 유효한 OpenAI 모델 (2025년 4월 출시). 오류 아님

### Stage 1 프롬프트 보류 항목 (사용자 명시적 보류)

- `MAIN_LABEL_EN`, `COUNTER_HISTORY` 변수가 DERIVED RULES에 정의되어 있으나 프롬프트 본문에서 미사용
- `DATE_RANGE`가 `news_report` 전용으로 기술되어 있으나 실제로는 1-C/1-D에서도 활용

---

## 다음 단계 제안

1. **Stage 1 보류 항목 재논의** — 미사용 변수 정리, DATE_RANGE 범위 명확화
2. **파일명 `aggresive_debator.py` 변경 여부** — 사용자가 현재 보류 지시했으므로 별도 확인 필요
3. **graph/prompts/ 내 프롬프트 템플릿 검토** — `introduction.txt`, `main_body.txt`, `conclusion.txt`의 heading 계층 불일치 및 한영 혼용 표현 (탐색 시 식별했으나 아직 상세 리뷰/수정 미진행)
