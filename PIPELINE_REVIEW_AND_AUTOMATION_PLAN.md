# 유가 전망 보고서 파이프라인 — 전체 검토 및 자동화 계획

> 작성일: 2026-02-10
> 목적: Stage 0/1/2 프롬프트 로직 검토 + Stage 1/2 자동화 설계

---

## Context

현재 브렌트유 전망 보고서 생성은 3단계로 나뉘어 있다:
- **Stage 0**: Python LangGraph 멀티에이전트 (자동) → `full_states_log.json`
- **Stage 1**: ChatGPT 수동 프롬프트 (GPT-5.2) → `stage1_result.md` (1-A, 1-B, 1-C/1-D)
- **Stage 2**: ChatGPT 수동 프롬프트 (GPT-5.2) → 최종 한국어 보고서

**최종 목표**: Stage 1, 2를 Python 코드에 통합하여 `main.py` 한 번 실행으로 Stage 0 → 1 → 2 전체 파이프라인을 자동화한다.

**LLM 선택**: 기존 Stage 0과 동일한 config 사용 (deep_think: o3, quick_think: gpt-4.1)
**웹 검색**: 기존 News Analyst와 동일한 OpenAI web search API 활용 + 도메인 화이트리스트 필터

---

## PART 1: 프롬프트 검토 — 발견된 이슈 및 개선안

### Stage 0 이슈 (7건)

| # | 이슈 | 심각도 | 개선안 |
|---|------|--------|--------|
| S0-1 | Social Media Analyst: 8개 사이트 하드코딩 (`wealthtrend.net`, `spglobal.com` 등) | LOW | `config["social_media_sources"]`로 설정화 |
| S0-2 | Bull/Bear 토론: 매 턴마다 4개 리포트 전문 재주입 → 토큰 낭비, 반복 논점 | MED | 2라운드 이후부터 500토큰 요약본으로 교체하는 `_summarize_reports()` 헬퍼 추가 |
| S0-3 | BaseWriter(`introduction.txt`/`main_body.txt`/`conclusion.txt`) 출력이 Stage 1/2와 완전 분리 — 두 개의 독립된 보고서 시스템이 공존 | HIGH | ReportGraph로 대체 후 archive |
| S0-4 | Analyst 순차 실행 (Market→Social→News→Fundamentals) — 독립적인 3개를 직렬 처리 | LOW | Market/Social/News 3개 병렬화 가능 (별도 PR) |
| S0-5 | `default_config.py`의 `data_dir: "/Users"` 하드코딩 | LOW | 상대경로로 변경 |
| S0-6 | Fundamentals Analyst 프롬프트 내 한영 혼용 (변수 참조표가 한국어) | INFO | 의도적 설계 — 한국어 변수 설명이 하류 한국어 리포트 생성에 필요. 변경 불요 |
| S0-7 | `graph/prompts/*.txt` heading 계층 및 한영 혼용 (HANDOFF에서 미착수 언급) | LOW | ReportGraph 도입 시 archive 대상이므로 별도 수정 불요 |

### Stage 1 이슈 (6건)

| # | 이슈 | 심각도 | 개선안 |
|---|------|--------|--------|
| S1-1 | `MAIN_LABEL_EN`, `COUNTER_HISTORY` — DERIVED RULES에 정의되었으나 프롬프트 본문에서 한 번도 참조되지 않음 | LOW | 자동화 시 DERIVED RULES에서 제거 (코드에서 불필요한 변수 생성 안 함) |
| S1-2 | `DATE_RANGE`가 "news_report 전용"으로 기술되어 있으나, 실제로는 1-C/1-D 서술에서도 관측 범위로 사용됨 | MED | 자동화 코드에서 DATE_RANGE를 Stage 1 전체 관측 범위로 명확히 재정의 |
| S1-3 | High-Impact Sweep (A~D 카테고리 gap-fill)이 웹 검색 기능 필요 — ChatGPT에서는 내장, 자동화 시 별도 구현 필요 | HIGH | 새로운 `search_whitelist_news` 도구를 Toolkit에 추가 |
| S1-4 | 단일 ChatGPT 턴에서 3개 작업(1-A, 1-B, 1-C/1-D)을 한꺼번에 수행하는 설계 → 멀티에이전트로 분해해야 품질 관리 가능 | HIGH | 3개 에이전트(1-A, 1-B, 1-CD)로 분리, 각각 독립된 프롬프트와 LLM 할당 |
| S1-5 | "최근 30일" DATE_RANGE가 "오늘" 기준으로 자동 생성 → 실행일(trade_date)과 불일치 가능 | MED | Variable Resolver에서 `trade_date` 기준으로 계산하도록 변경 |
| S1-6 | Stage 1 HORIZON "향후 1개월" ↔ Stage 2 REPORT_HORIZON "향후 1주일" 시간축 차이 | INFO | 의도적 설계 (1개월 관측 → 1주일 결론 압축). 코드에서 `horizon_1m`과 `report_horizon` 명시적 분리로 처리 |

### Stage 2 이슈 (7건)

| # | 이슈 | 심각도 | 개선안 |
|---|------|--------|--------|
| S2-1 | 외부 증거 수집(External Evidence Collection)에 화이트리스트 제한 웹 검색 필요 | HIGH | `search_whitelist_news` + `verify_url` 도구 구현 |
| S2-2 | 링크 검증 게이트 — URL이 실제 기사/보고서 페이지인지 확인 필요 (허브/프로필/접근불가 폐기) | HIGH | `verify_url` 도구: HEAD 요청 + 콘텐츠 타입 확인 + 제목 추출 |
| S2-3 | `{scenario_label}` / `{scenario_label_counter}` 미정의 변수 | DONE | HANDOFF에서 `{MAIN_SCENARIO}`/`{COUNTER_SCENARIO}`로 이미 수정됨 |
| S2-4 | BASE_PRICE 레이블 "(내부 AI)" → "(시장 데이터)" | DONE | HANDOFF에서 이미 수정됨 |
| S2-5 | 참고문헌 10~20개 요구 → 자동 검증 필요 | MED | Report Validator 노드에서 프로그래밍적 검증 + 미달 시 재실행 |
| S2-6 | lexicon 파일(`oil_market_lexicon_v3.json`, 554줄) 로딩 및 규칙 적용 — 프롬프트에 전체 삽입 필요 | HIGH | Variable Resolver에서 JSON 로드 → Stage 2 시스템 프롬프트에 주입 |
| S2-7 | `2-1~~2-3` 이중 물결표 / 섹션번호 중복 / 단위 "10장이내" | DONE | HANDOFF에서 모두 수정됨 |

### Cross-Stage 이슈 (5건)

| # | 이슈 | 개선안 |
|---|------|--------|
| CS-1 | Stage 0 출력 → Stage 1 입력 → Stage 2 입력: 모두 수동 복사/붙여넣기 | ReportGraph가 Stage 0 출력 dict를 직접 소비, 자동 연결 |
| CS-2 | BASE_PRICE / FORECAST_PRICE를 `daily_predictions.csv`에서 수동 조회 | Variable Resolver가 CSV 자동 읽기 → `y_base`, `prediction` 평균 계산 |
| CS-3 | MAIN_SCENARIO ("상승"/"하락") 수동 판단 | Variable Resolver에서 자동: `"하락" if forecast < base else "상승"` |
| CS-4 | Stage 0 News Analyst (광범위 뉴스 수집) ↔ Stage 1/2 (뉴스 재검색) 중복 우려 | 상호 보완적 — Stage 0은 광범위 수집, Stage 1/2는 고충격 이벤트(A~D) gap-fill. 양쪽 유지 |
| CS-5 | BaseWriter 보고서(bullet 중심, 기술지표 포함)와 Stage 1/2 보고서(문단형, 기술지표 금지) 이원화 | ReportGraph로 통합, BaseWriter archive |

---

## PART 2: 자동화 아키텍처

### 새로운 ReportGraph 워크플로우

```
[Stage 0 완료 — full_states_log dict]
       │
       ▼
┌─────────────────────┐
│  Variable Resolver   │  ← daily_predictions.csv + lexicon.json 로드
│  (순수 함수, LLM 없음) │  ← MAIN_SCENARIO / BASE_PRICE / FORECAST_PRICE / DATE_RANGE 자동 계산
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Stage 1-A Agent     │  ← fundamentals_report 해석 + QC 요약 (deep_think / o3)
│  [1-A 결과]          │  ← 입력: fundamentals_report
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Stage 1-B Agent     │  ← fundamentals 한국어 표 생성 — w/w% > 5% 변수만 (quick_think / gpt-4.1)
│  [1-B 결과]          │  ← 입력: fundamentals_report
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Stage 1-CD Agent    │  ← 시나리오 내러티브 + High-Impact Sweep (deep_think / o3 + 웹검색 도구)
│  [1-C/1-D 결과]      │  ← 입력: 5개 자료(fundamentals, news, final_trade_decision, bull/bear_history)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Stage1 Combiner     │  ← 1-A + 1-B + 1-CD 결합 (순수 함수)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Msg Clear           │  ← 메시지 히스토리 초기화 (기존 create_msg_delete 패턴)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Stage 2 Writer      │  ← 최종 보고서 생성 + 외부 증거 수집 (deep_think / o3 + 웹검색/URL검증 도구)
│                      │  ← 입력: stage1_combined + lexicon + variables
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Report Validator    │  ← lexicon 규칙 검증, 참고문헌 수, 금지어, 섹션 구조 체크 (순수 함수)
└─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│  [조건부] 참고문헌 < 10개?  │──Yes──→ Stage 2 Writer 재실행 (최대 1회)
└────────────────────────────┘
       │ No
       ▼
┌─────────────────────┐
│  Output Writer       │  ← .md 파일 저장 (순수 함수)
└─────────────────────┘
```

### 새로운 ReportState (상태 정의)

```python
# marketagents/agents/utils/report_states.py

from typing import Annotated, Dict, List
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


class ReportVariables(TypedDict):
    main_scenario: str        # "상승" or "하락"
    counter_scenario: str     # 반대
    base_price: float         # y_base (최근 종가)
    forecast_price: float     # prediction 5일 평균
    date_range: str           # "최근 1개월(YYYY-MM-DD~YYYY-MM-DD)"
    report_horizon: str       # "향후 1주일" (고정, Stage 2용)
    horizon_1m: str           # "향후 1개월" (고정, Stage 1용)
    trade_date: str           # 실행일


class ReportState(MessagesState):
    # Stage 0에서 가져오는 데이터
    market_report: Annotated[str, "Stage 0 Market Analyst output"]
    sentiment_report: Annotated[str, "Stage 0 Social Media Analyst output"]
    news_report: Annotated[str, "Stage 0 News Analyst output"]
    fundamentals_report: Annotated[str, "Stage 0 Fundamentals Analyst output"]
    bull_history: Annotated[str, "Bull debate history"]
    bear_history: Annotated[str, "Bear debate history"]
    final_trade_decision: Annotated[str, "Stage 0 Risk Manager decision"]
    investment_plan: Annotated[str, "Stage 0 Research Manager plan"]

    # 자동 계산 변수
    variables: Annotated[ReportVariables, "Auto-resolved report variables"]
    lexicon: Annotated[Dict, "oil_market_lexicon_v3.json contents"]

    # Stage 1 출력
    stage1_a: Annotated[str, "[1-A] fundamentals interpretation + QC"]
    stage1_b: Annotated[str, "[1-B] fundamentals Korean table"]
    stage1_cd: Annotated[str, "[1-C/1-D] Main scenario narrative"]
    stage1_combined: Annotated[str, "Full stage1 output concatenated"]

    # Stage 2 출력
    final_report: Annotated[str, "Complete final Korean report"]
    validation_result: Annotated[Dict, "Post-validation results"]
```

---

## PART 3: 새로 생성할 파일 목록

```
Code/oil_forecast_report/marketagents/
├── agents/
│   └── report/                                ← 새 디렉토리
│       ├── __init__.py
│       ├── variable_resolver.py               ← 변수 자동 계산 (순수 함수)
│       ├── stage1_fundamentals_interpreter.py  ← [1-A] 에이전트
│       ├── stage1_fundamentals_table.py        ← [1-B] 에이전트
│       ├── stage1_scenario_narrative.py        ← [1-C/1-D] 에이전트
│       ├── stage1_combiner.py                 ← Stage 1 결합 (순수 함수)
│       ├── stage2_report_writer.py            ← 최종 보고서 에이전트
│       └── report_validator.py                ← 검증 노드 (순수 함수)
├── agents/utils/
│   └── report_states.py                       ← ReportState / ReportVariables 정의
└── graph/
    └── report_graph.py                        ← ReportGraph 클래스 (메인 오케스트레이터)
```

## PART 4: 수정할 기존 파일

| 파일 | 변경 내용 |
|------|----------|
| `agents/utils/agent_utils.py` | `Toolkit`에 `search_whitelist_news`, `verify_url` 도구 추가 |
| `dataflows/interface.py` | `search_whitelist_news()`, `verify_url()` 백엔드 함수 추가 |
| `agents/__init__.py` | `report/` 모듈 export 추가 |
| `default_config.py` | 보고서 관련 설정 키 추가 |
| `main.py` | Stage 0 후 ReportGraph 실행 코드 추가 |

## PART 5: Archive 대상 (삭제 아닌 보관)

| 파일 | 사유 |
|------|------|
| `graph/prompts/introduction.txt` | ReportGraph의 Stage 1/2 프롬프트로 대체 |
| `graph/prompts/main_body.txt` | 동일 |
| `graph/prompts/conclusion.txt` | 동일 |
| `agents/writers/base_writer.py` | ReportGraph의 report agents로 대체 |

---

## PART 6: 에이전트별 LLM 할당

| 에이전트 | LLM | 근거 |
|---------|-----|------|
| Variable Resolver | 없음 (순수 함수) | LLM 불필요 — CSV 읽기 + JSON 로드 + 조건 분기 |
| Stage 1-A (Fundamentals 해석) | `deep_think` (o3) | 복잡한 한국어 분석 + QC 체크리스트 판단 |
| Stage 1-B (Fundamentals 표) | `quick_think` (gpt-4.1) | 구조화된 테이블 변환 — 분석보다 포맷팅 중심 |
| Stage 1-CD (시나리오 내러티브) | `deep_think` (o3) | 5개 소스 종합 + High-Impact 웹검색 + 문단형 서술 |
| Stage1 Combiner | 없음 (순수 함수) | 문자열 결합만 |
| Stage 2 Writer | `deep_think` (o3) | 전체 보고서 + lexicon 554줄 준수 + 외부 증거 수집 + 참고문헌 10~20개 |
| Report Validator | 없음 (순수 함수) | 정규식/문자열 매칭 기반 프로그래밍적 검증 |

---

## PART 7: 핵심 구현 세부사항

### 7-1. Variable Resolver — 변수 자동 계산

```python
# marketagents/agents/report/variable_resolver.py

def create_variable_resolver(predictions_csv_path: str, lexicon_json_path: str):
    def resolve_variables(state: ReportState) -> dict:
        import pandas as pd
        import json
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        # 1. 예측값 로드
        df = pd.read_csv(predictions_csv_path)
        base_price = round(df['y_base'].iloc[0], 2)
        forecast_price = round(df['prediction'].iloc[:5].mean(), 2)

        # 2. 시나리오 자동 결정
        main_scenario = "하락" if forecast_price < base_price else "상승"
        counter_scenario = "상승" if main_scenario == "하락" else "하락"

        # 3. DATE_RANGE: trade_date 기준 1개월 전
        trade_date = state.get("trade_date", datetime.now().strftime("%Y-%m-%d"))
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - relativedelta(months=1)
        date_range = f"최근 1개월({start_date:%Y-%m-%d}~{end_date:%Y-%m-%d})"

        # 4. Lexicon 로드
        with open(lexicon_json_path, 'r', encoding='utf-8') as f:
            lexicon = json.load(f)

        variables = {
            "main_scenario": main_scenario,
            "counter_scenario": counter_scenario,
            "base_price": base_price,
            "forecast_price": forecast_price,
            "date_range": date_range,
            "report_horizon": "향후 1주일",
            "horizon_1m": "향후 1개월",
            "trade_date": trade_date,
        }

        return {"variables": variables, "lexicon": lexicon}

    return resolve_variables
```

### 7-2. search_whitelist_news 도구

기존 `get_global_news_openai` 패턴(`agent_utils.py:384~398`)을 따르되, 도메인 필터 추가:

```python
# agent_utils.py — Toolkit 클래스에 추가

@staticmethod
@tool
def search_whitelist_news(
    query: Annotated[str, "Search query for oil market news"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
    """화이트리스트 도메인에서만 유가 시장 뉴스를 검색합니다.
    허용 도메인: reuters.com, bloomberg.com, wsj.com, ft.com,
    iea.org, eia.gov, opec.org 등.
    Returns: URL, 매체명, 날짜, 제목, 요약 1문장 포맷."""
    results = interface.search_whitelist_news(query, curr_date, 30)
    return results

@staticmethod
@tool
def verify_url(
    url: Annotated[str, "URL to verify"],
) -> str:
    """URL이 실제 기사/보고서 페이지인지 검증합니다.
    허브/프로필/접근불가 페이지는 실패로 반환합니다."""
    results = interface.verify_url(url)
    return results
```

### 7-3. Stage 2 프롬프트 빌더

Stage 2 프롬프트 원문(670줄, `report_creation_Prompt_stage2_2026-01-26.md`)을 Python 함수로 변환:

```python
# marketagents/agents/report/stage2_report_writer.py

def _build_stage2_system_prompt(variables: dict, lexicon: dict) -> str:
    """Stage 2 프롬프트 전문을 변수 치환하여 생성.
    프롬프트의 [0]~[10] 섹션 구조를 그대로 유지하되,
    {MAIN_SCENARIO}, {BASE_PRICE} 등을 실제 값으로 치환."""

    import json
    v = variables
    lexicon_str = json.dumps(lexicon, ensure_ascii=False, indent=2)

    prompt = f"""[0] PARAMETERS
MAIN_SCENARIO = {v['main_scenario']}
COUNTER_SCENARIO = {v['counter_scenario']}
DATE_RANGE = {v['date_range']}
REPORT_HORIZON = {v['report_horizon']}
BASE_PRICE = {v['base_price']}
FORECAST_PRICE = {v['forecast_price']}
IA_TAG = [IA1]

[1] INPUTS
oil_market_lexicon:
{lexicon_str}

[2] SCENARIO AUTO-SET RULE
... (Stage 2 프롬프트 [2]~[10] 원문 그대로)
"""
    return prompt
```

### 7-4. Report Validator 검증 항목

```python
# marketagents/agents/report/report_validator.py — LLM 불필요, 프로그래밍적 검증

def create_report_validator():
    def validate_report(state: ReportState) -> dict:
        report = state["final_report"]
        lexicon = state["lexicon"]
        v = state["variables"]
        issues = []

        # 1. 금지 패턴 (lexicon.prohibited_patterns)
        for category, patterns in lexicon["style_guide"]["prohibited_patterns"].items():
            for pattern in patterns:
                if pattern in report:
                    issues.append(f"금지 패턴 ({category}): '{pattern}'")

        # 2. 참고문헌 수: 10 ≤ count ≤ 20
        import re
        ref_count = len(re.findall(r'^\[\d+\]', report, re.MULTILINE))
        if ref_count < 10:
            issues.append(f"참고문헌 부족: {ref_count} < 10")
        if ref_count > 20:
            issues.append(f"참고문헌 초과: {ref_count} > 20")

        # 3. [IA1] 태그 존재 확인
        ia1_count = report.count("[IA1]")
        if ia1_count < 2:
            issues.append(f"[IA1] 태그 부족: {ia1_count}개 (최소 2개 필요)")

        # 4. 필수 섹션 존재
        required = ["시장 개요", "2-1", "2-2", "2-3", "제한적", "시장 해석", "참고"]
        for section in required:
            if section not in report:
                issues.append(f"필수 섹션 누락: '{section}'")

        # 5. "향후 1주일 브렌트유 시장" 문구 확인 (1장/4장)
        if report.count("향후 1주일 브렌트유 시장") < 1:
            issues.append("'향후 1주일 브렌트유 시장' 문구 미포함")

        # 6. 본문 1~4장에서 리스트형 표현 탐지
        # 7. 문장 종결어미: forbidden 매칭

        return {"validation_result": {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "ref_count": ref_count,
        }}

    return validate_report
```

### 7-5. 업데이트된 main.py

```python
from marketagents.graph.trading_graph import MarketAgentsGraph
from marketagents.graph.report_graph import ReportGraph
from marketagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()
config = DEFAULT_CONFIG.copy()

# ── Stage 0: 멀티에이전트 분석 ──
ma = MarketAgentsGraph(debug=False, config=config)
target_date = "2026-01-26"
final_state, decision = ma.propagate("Brent crude oil price", target_date)
print("[DECISION]", decision)

# ── Stage 1 + 2: 보고서 자동 생성 ──
rg = ReportGraph(config=config)
stage0_output = ma.log_states_dict[target_date]
report_result = rg.generate_report(stage0_output, target_date)

# ── 저장 ──
with open(f"reports/SKT_유가전망_AI모델_전망리포트_브렌트유_{target_date}.md", "w") as f:
    f.write(report_result["final_report"])

print("[VALIDATION]", report_result["validation_result"])
```

### 7-6. ReportGraph 클래스 구조

```python
# marketagents/graph/report_graph.py

class ReportGraph:
    """Stage 1 + Stage 2 보고서 생성 오케스트레이터.
    Stage 0의 MarketAgentsGraph와 별도의 그래프로 운영."""

    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        self.deep_thinking_llm = ...   # trading_graph.py와 동일 패턴
        self.quick_thinking_llm = ...
        self.toolkit = Toolkit(config=self.config)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ReportState)

        # 노드 추가
        workflow.add_node("Variable Resolver", create_variable_resolver(...))
        workflow.add_node("Stage1-A", create_fundamentals_interpreter(self.deep_thinking_llm))
        workflow.add_node("Stage1-B", create_fundamentals_table(self.quick_thinking_llm))
        workflow.add_node("Stage1-CD", create_scenario_narrative(self.deep_thinking_llm, self.toolkit))
        workflow.add_node("Stage1 Combiner", create_stage1_combiner())
        workflow.add_node("Msg Clear", create_msg_delete())
        workflow.add_node("Stage2 Writer", create_stage2_report_writer(self.deep_thinking_llm, self.toolkit))
        workflow.add_node("Validator", create_report_validator())

        # 엣지 연결
        workflow.add_edge(START, "Variable Resolver")
        workflow.add_edge("Variable Resolver", "Stage1-A")
        workflow.add_edge("Stage1-A", "Stage1-B")
        workflow.add_edge("Stage1-B", "Stage1-CD")
        # Stage1-CD는 웹검색 도구 사용 가능 → 조건부 엣지 (기존 should_continue_* 패턴)
        workflow.add_edge("Stage1-CD", "Stage1 Combiner")
        workflow.add_edge("Stage1 Combiner", "Msg Clear")
        workflow.add_edge("Msg Clear", "Stage2 Writer")
        # Stage2 Writer도 웹검색 도구 사용 가능 → 조건부 엣지
        workflow.add_edge("Stage2 Writer", "Validator")
        workflow.add_edge("Validator", END)

        return workflow.compile()

    def generate_report(self, stage0_output: dict, trade_date: str) -> dict:
        """Stage 0 출력 dict를 받아 최종 보고서를 생성."""
        initial_state = self._create_initial_state(stage0_output, trade_date)
        return self.graph.invoke(initial_state, config={"recursion_limit": 50})

    def _create_initial_state(self, stage0_output: dict, trade_date: str) -> dict:
        """Stage 0 로그에서 ReportState 초기값을 추출."""
        return {
            "messages": [("human", "Generate oil forecast report")],
            "market_report": stage0_output.get("market_report", ""),
            "sentiment_report": stage0_output.get("sentiment_report", ""),
            "news_report": stage0_output.get("news_report", ""),
            "fundamentals_report": stage0_output.get("fundamentals_report", ""),
            "bull_history": stage0_output.get("investment_debate_state", {}).get("bull_history", ""),
            "bear_history": stage0_output.get("investment_debate_state", {}).get("bear_history", ""),
            "final_trade_decision": stage0_output.get("final_trade_decision", ""),
            "investment_plan": stage0_output.get("investment_plan", ""),
            "trade_date": trade_date,
        }
```

### 7-7. default_config.py 추가 설정

```python
DEFAULT_CONFIG = {
    # ... 기존 키 유지 ...

    # Report generation (신규)
    "predictions_csv_path": "input_data/Model/latest/daily_predictions.csv",
    "lexicon_json_path": "Prompt/latest/oil_market_lexicon_v3.json",
    "report_output_dir": "./reports",
    "social_media_sources": [
        "wealthtrend.net", "spglobal.com", "oilprice.com",
        "monetamarkets.com", "fxempire.com", "argusmedia.com",
        "genspark.ai", "qcintel.com"
    ],
    "evidence_whitelist": [
        "reuters.com", "apnews.com", "bloomberg.com", "wsj.com", "ft.com",
        "nytimes.com", "bbc.com", "iea.org", "eia.gov", "opec.org",
        "imf.org", "worldbank.org", "investing.com"
    ],
    "min_references": 10,
    "max_references": 20,
    "max_report_retries": 1,
}
```

---

## PART 8: 구현 순서 (7단계)

| 단계 | 내용 | 산출물 | 검증 방법 |
|------|------|--------|----------|
| **1. 기반** | `report_states.py`, `variable_resolver.py`, 스켈레톤 `report_graph.py` | 변수 자동 계산 동작 | 기존 `full_states_log_2026-01-26.json` + `daily_predictions.csv`에서 변수 정확히 계산되는지 확인 |
| **2. Stage 1 에이전트** | `stage1_fundamentals_interpreter.py`, `stage1_fundamentals_table.py`, `stage1_scenario_narrative.py`, `stage1_combiner.py` | Stage 1 결과물 | 기존 `stage1_result_2026-01-26.md`와 품질 비교 |
| **3. 웹 검색 도구** | `Toolkit` 확장 (`search_whitelist_news`, `verify_url`) + `interface.py` 함수 | 도구 동작 확인 | High-Impact Sweep 쿼리 (예: "OPEC+ policy delay oil 2026") 테스트 |
| **4. Stage 2 에이전트** | `stage2_report_writer.py` + `_build_stage2_system_prompt()` | 최종 보고서 초안 | 기존 최종 보고서(`SKT_유가전망_...2026-01-26.md`)와 구조/품질 비교 |
| **5. 검증 + 통합** | `report_validator.py` + `report_graph.py` 완성 + 조건부 재실행 로직 | E2E 테스트 | `full_states_log` JSON → 최종 보고서 .md 생성 확인 |
| **6. End-to-End** | `main.py` 업데이트 + `default_config.py` 확장 | 완전 자동화 | `python main.py` 한 번 실행으로 Stage 0 → 1 → 2 → 파일 저장 |
| **7. Stage 0 개선** (별도 PR) | Bull/Bear 요약 헬퍼(S0-2), Social Media 설정화(S0-1) | 토큰 절감 + 유연성 | 기존 동작 유지 + 토큰 사용량 비교 |

---

## PART 9: 주요 설계 결정 사항

### Q1: Stage 0 그래프에 Stage 1/2를 합치는가 vs 별도 그래프?

**결정: 별도 그래프 (`ReportGraph`)**

이유:
- Stage 0은 `AgentState` 사용, Stage 1/2는 `ReportState` 필요 (변수 구조가 다름)
- Stage 0 실행 없이 기존 JSON에서 Stage 1/2만 재실행 가능해야 함 (디버깅, 프롬프트 튜닝)
- 독립적 테스트/배포 가능
- `main.py`에서 순차 호출로 간단히 연결

### Q2: 기존 BaseWriter/WritingGraph는?

**결정: Archive** — ReportGraph가 완전 대체

BaseWriter는 bullet 중심 + 기술지표 포함 형식이고, Stage 1/2는 문단형 + 기술지표 금지이므로 양립 불가. ReportGraph가 최종 보고서 생성을 전담.

### Q3: deep_think vs quick_think 선택 기준?

**결정:**
- 복잡한 분석/종합/서술 → `deep_think` (o3): Stage 1-A, 1-CD, Stage 2
- 구조화된 추출/포맷 변환 → `quick_think` (gpt-4.1): Stage 1-B

### Q4: Stage 2의 외부 증거 수집 방식?

**결정: 도구 호출 (tool-use loop) — 기존 패턴 재사용**

기존 `setup.py`의 Analyst → ToolNode → Analyst 루프와 동일:
1. LLM이 `search_whitelist_news` 도구 호출 결정
2. `ToolNode`가 실행 → 결과 반환
3. LLM이 결과를 본문에 통합
4. `should_continue_*` 조건부 로직으로 도구 루프 제어
5. 도구 호출 없으면 다음 노드로 진행

### Q5: Stage 1-CD의 High-Impact Sweep 범위?

**결정: Stage 0 News Analyst가 이미 수집한 뉴스 + 추가 gap-fill**

- Stage 0의 `news_report`에 A~D 카테고리(산유국 이슈, 해상물류, 소비국 정책, 국제기구 전망)가 있으면 → 그대로 사용
- 없거나 일부만 있으면 → `search_whitelist_news` 도구로 추가 검색
- 검색 범위: DATE_RANGE (기본 1개월), 국제기구 전망은 3개월까지 확장

---

## 참고: 기존 코드 패턴 (재사용 대상)

| 패턴 | 파일 위치 | 재사용 방식 |
|------|----------|------------|
| `create_*()` 팩토리 함수 | 모든 agent 파일 | 모든 새 에이전트도 동일 패턴 |
| `create_msg_delete()` | `agent_utils.py:18~31` | Stage 1 → Stage 2 사이 메시지 초기화에 그대로 사용 |
| `Toolkit` 클래스 + `@staticmethod @tool` | `agent_utils.py:34~420` | 새 도구도 동일 데코레이터 패턴 |
| `GraphSetup.setup_graph()` | `setup.py:42~204` | `ReportGraph._build_graph()`의 모델 |
| `MarketAgentsGraph.__init__()` LLM 초기화 | `trading_graph.py:60~70` | `ReportGraph.__init__()` 동일 로직 |
| `Propagator.create_initial_state()` | `propagation.py` | `ReportGraph._create_initial_state()` 참고 |
| `_log_state()` JSON 저장 | `trading_graph.py:193~229` | Output Writer에서 유사 패턴 |
| `ConditionalLogic.should_continue_*` | `conditional_logic.py` | Stage 1-CD, Stage 2 도구 루프 제어 |
