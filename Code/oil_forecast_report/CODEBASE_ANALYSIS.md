# Oil Forecast Report - 코드베이스 분석

## 1. 개요

이 프로젝트는 **Brent 원유 가격 예측 및 투자 의사결정**을 위한 멀티 에이전트 시스템입니다. LangGraph를 기반으로 여러 AI 에이전트가 협업하여 시장 분석, 투자 토론, 리스크 평가를 수행하고 최종 거래 결정(BUY/SELL/HOLD)을 도출합니다.

### 핵심 특징
- **멀티 에이전트 아키텍처**: 다양한 전문 에이전트들이 협업
- **토론 기반 의사결정**: Bull/Bear 연구원 간 토론, 리스크 분석가 간 토론
- **메모리 기반 학습**: 과거 유사 상황에서의 교훈을 활용
- **다중 데이터 소스**: 시장 데이터, 뉴스, 소셜 미디어, 펀더멘털 분석

---

## 2. 프로젝트 구조

```
oil_forecast_report/
├── main.py                          # 진입점
├── eval_results/                    # 평가 결과 저장
└── marketagents/
    ├── default_config.py            # 기본 설정
    ├── agents/                      # 에이전트 정의
    │   ├── __init__.py              # 에이전트 모듈 export
    │   ├── analysts/                # 분석가 에이전트
    │   │   ├── market_analyst.py    # 시장 분석가
    │   │   ├── news_analyst.py      # 뉴스 분석가
    │   │   ├── social_media_analyst.py  # 소셜 미디어 분석가
    │   │   └── fundamentals_analyst.py  # 펀더멘털 분석가
    │   ├── researchers/             # 연구원 에이전트
    │   │   ├── bull_researcher.py   # 강세 연구원
    │   │   └── bear_researcher.py   # 약세 연구원
    │   ├── risk_mgmt/               # 리스크 관리 에이전트
    │   │   ├── aggresive_debator.py # 공격적 분석가
    │   │   ├── conservative_debator.py  # 보수적 분석가
    │   │   └── neutral_debator.py   # 중립적 분석가
    │   ├── managers/                # 관리자 에이전트
    │   │   ├── research_manager.py  # 연구 관리자
    │   │   └── risk_manager.py      # 리스크 관리자
    │   ├── trader/                  # 트레이더 에이전트
    │   │   └── trader.py
    │   ├── writers/                 # 작성 에이전트
    │   │   └── base_writer.py
    │   └── utils/                   # 유틸리티
    │       ├── agent_states.py      # 상태 정의
    │       ├── agent_utils.py       # 도구 및 유틸리티
    │       └── memory.py            # 메모리 시스템
    ├── dataflows/                   # 데이터 처리
    │   ├── interface.py             # 데이터 인터페이스
    │   ├── config.py                # 데이터 설정
    │   ├── yfin_utils.py            # Yahoo Finance 유틸리티
    │   ├── googlenews_utils.py      # Google News 유틸리티
    │   ├── reddit_utils.py          # Reddit 유틸리티
    │   └── utils.py                 # 일반 유틸리티
    └── graph/                       # 그래프 워크플로우
        ├── __init__.py
        ├── trading_graph.py         # 메인 그래프 클래스
        ├── setup.py                 # 그래프 설정
        ├── propagation.py           # 상태 전파
        ├── conditional_logic.py     # 조건부 로직
        ├── signal_processing.py     # 시그널 처리
        └── prompts/                 # 프롬프트 템플릿
            ├── introduction.txt
            ├── main_body.txt
            └── conclusion.txt
```

---

## 3. 아키텍처 및 워크플로우

### 3.1 전체 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT                                          │
│                  Company Name + Trade Date                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DATA ANALYSIS                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │   Market     │ │   Social     │ │    News      │ │ Fundamentals │    │
│  │   Analyst    │ │   Analyst    │ │   Analyst    │ │   Analyst    │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│         │                │                │                │             │
│         ▼                ▼                ▼                ▼             │
│  market_report    sentiment_report   news_report   fundamentals_report  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: INVESTMENT DEBATE                            │
│         ┌─────────────────┐     ┌─────────────────┐                     │
│         │ Bull Researcher │ ◄─► │ Bear Researcher │                     │
│         │  (강세 주장)     │     │  (약세 주장)     │                     │
│         └─────────────────┘     └─────────────────┘                     │
│                         │                                                │
│                         ▼                                                │
│                ┌─────────────────┐                                       │
│                │Research Manager │ → investment_plan                     │
│                │  (토론 결론)     │                                       │
│                └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: TRADING DECISION                             │
│                ┌─────────────────┐                                       │
│                │     Trader      │ → trader_investment_plan              │
│                └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: RISK ASSESSMENT                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                     │
│  │Risky Analyst │ │ Safe Analyst │ │Neutral Analyst│                    │
│  │ (공격적)      │ │ (보수적)      │ │ (중립적)       │                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                     │
│         │                │                │                              │
│         └────────────────┼────────────────┘                              │
│                          ▼                                               │
│                ┌─────────────────┐                                       │
│                │  Risk Manager   │ → final_trade_decision                │
│                │  (최종 결정)     │                                       │
│                └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT                                         │
│               Signal Processing → BUY / SELL / HOLD                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 LangGraph 상태 머신

워크플로우는 `StateGraph`를 사용하여 구현됩니다:

```python
# setup.py에서 정의된 그래프 구조
START → Market Analyst → tools_market ↔ Market Analyst
                              ↓
                    Msg Clear Market
                              ↓
Social Analyst → tools_social ↔ Social Analyst → Msg Clear Social
                              ↓
News Analyst → tools_news ↔ News Analyst → Msg Clear News
                              ↓
Fundamentals Analyst → ... → Bull Researcher ↔ Bear Researcher
                              ↓
                    Research Manager
                              ↓
                         Trader
                              ↓
          Risky Analyst → Safe Analyst → Neutral Analyst
                              ↓
                      Risk Manager → END
```

---

## 4. 핵심 컴포넌트 상세

### 4.1 MarketAgentsGraph (trading_graph.py)

메인 오케스트레이터 클래스입니다.

```python
class MarketAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(self, selected_analysts, debug, config):
        # LLM 초기화 (deep_thinking_llm, quick_thinking_llm)
        # 메모리 초기화 (bull, bear, trader, research_manager, risk_manager)
        # 도구 노드 생성
        # 그래프 설정 및 컴파일

    def propagate(self, company_name, trade_date):
        # 초기 상태 생성
        # 그래프 실행
        # 결과 로깅
        # 최종 결정 반환
```

**주요 기능:**
- 다중 LLM 제공자 지원 (OpenAI, Anthropic, Google)
- Deep thinking LLM (o3)과 Quick thinking LLM (gpt-4.1) 구분
- 5개의 독립적인 메모리 시스템

### 4.2 상태 정의 (agent_states.py)

```python
class AgentState(MessagesState):
    company_of_interest: str    # 분석 대상
    trade_date: str             # 거래 날짜

    # 분석 리포트
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str

    # 토론 상태
    investment_debate_state: InvestDebateState
    investment_plan: str

    # 트레이더 결정
    trader_investment_plan: str

    # 리스크 토론 상태
    risk_debate_state: RiskDebateState
    final_trade_decision: str

class InvestDebateState(TypedDict):
    bull_history: str           # 강세 토론 기록
    bear_history: str           # 약세 토론 기록
    history: str                # 전체 토론 기록
    current_response: str       # 최신 응답
    count: int                  # 토론 라운드 수

class RiskDebateState(TypedDict):
    risky_history: str          # 공격적 분석 기록
    safe_history: str           # 보수적 분석 기록
    neutral_history: str        # 중립적 분석 기록
    latest_speaker: str         # 마지막 발언자
    count: int                  # 토론 라운드 수
```

### 4.3 분석가 에이전트 (analysts/)

#### Market Analyst
- **역할**: 기술적 지표 분석
- **데이터 소스**: `AA-OIL_BRENT.csv` (최근 250일 가격 데이터)
- **분석 지표**: SMA, EMA, MACD, RSI, Bollinger Bands, ATR, VWMA
- **출력**: 8개 지표를 포함한 마크다운 테이블

#### News Analyst
- **역할**: 글로벌 뉴스 및 거시경제 분석
- **도구**: `get_global_news_openai`, `get_google_news`
- **출력 형식**: 날짜, 이벤트, Net Impact (%), 근거, 소스 테이블

#### Social Media Analyst
- **역할**: 금융 웹사이트에서 소셜 센티먼트 수집
- **대상 소스**: wealthtrend.net, spglobal.com, oilprice.com 등 8개 사이트
- **출력 형식**: Net Sentiment (%) 스코어링 (-100% ~ +100%)

#### Fundamentals Analyst
- **역할**: 펀더멘털 변수 분석
- **데이터 소스**: `recent_x_data.csv`
- **분석 항목**: 포지셔닝 데이터, 재고, 스프레드, 운임지수 등 40+ 변수
- **출력 형식**: 주간 변화율(w/w %) 포함 테이블

### 4.4 연구원 에이전트 (researchers/)

#### Bull Researcher
- **역할**: 투자 찬성 논거 제시
- **초점**: 성장 잠재력, 경쟁 우위, 긍정적 지표
- **특징**: 과거 유사 상황 메모리 활용

#### Bear Researcher
- **역할**: 투자 반대 논거 제시
- **초점**: 리스크, 구조적 문제, 부정적 지표
- **특징**: Bull Researcher와 토론 형식으로 상호작용

### 4.5 리스크 관리 에이전트 (risk_mgmt/)

| 에이전트 | 역할 | 관점 |
|---------|------|------|
| Risky Analyst | 고위험/고수익 옹호 | 공격적 투자 전략 |
| Safe Analyst | 자산 보호 우선 | 보수적/방어적 전략 |
| Neutral Analyst | 균형 잡힌 시각 | 양측 비판 및 중재 |

### 4.6 관리자 에이전트 (managers/)

#### Research Manager
- Bull/Bear 토론 평가
- 투자 계획 수립 (Buy/Sell/Hold)
- 과거 실수에서 학습

#### Risk Manager
- 3자 리스크 토론 평가
- 최종 거래 결정 도출
- 트레이더 계획 수정 및 확정

### 4.7 메모리 시스템 (memory.py)

```python
class FinancialSituationMemory:
    """ChromaDB 기반 시맨틱 메모리 시스템"""

    def __init__(self, name, config):
        # OpenAI 임베딩 (text-embedding-3-small)
        # ChromaDB 벡터 저장소

    def add_situations(self, situations_and_advice):
        # (상황, 조언) 튜플 리스트 저장
        # 임베딩 생성 및 저장

    def get_memories(self, current_situation, n_matches=1):
        # 현재 상황과 유사한 과거 경험 검색
        # 유사도 점수와 함께 반환
```

---

## 5. 설정 및 구성

### 5.1 기본 설정 (default_config.py)

```python
DEFAULT_CONFIG = {
    "project_dir": "...",
    "results_dir": "./results",
    "data_dir": "/Users",
    "data_cache_dir": ".../dataflows/data_cache",

    # LLM 설정
    "llm_provider": "openai",
    "deep_think_llm": "o3",           # 심층 분석용
    "quick_think_llm": "gpt-4.1",     # 빠른 처리용
    "backend_url": "https://api.openai.com/v1",

    # 토론 설정
    "max_debate_rounds": 2,           # Bull-Bear 토론 라운드
    "max_risk_discuss_rounds": 1,     # 리스크 토론 라운드
    "max_recur_limit": 100,

    # 도구 설정
    "online_tools": True,
}
```

### 5.2 지원 LLM 제공자

| 제공자 | Deep Think | Quick Think |
|--------|-----------|-------------|
| OpenAI | o3 | gpt-4.1 |
| Anthropic | (configurable) | (configurable) |
| Google | Gemini | Gemini |
| Ollama | (local) | (local) |
| OpenRouter | (proxy) | (proxy) |

---

## 6. 데이터 플로우

### 6.1 외부 데이터 소스

| 소스 | 용도 | 함수 |
|------|------|------|
| Yahoo Finance | 주가 데이터 | `get_YFin_data_online()` |
| Google News | 뉴스 검색 | `get_google_news()` |
| OpenAI Web Search | 글로벌 뉴스 | `get_global_news_openai()` |
| OpenAI Web Search | 종목 뉴스 | `get_stock_news_openai()` |

### 6.2 로컬 데이터 소스

| 파일 | 용도 |
|------|------|
| `AA-OIL_BRENT.csv` | Brent 원유 일별 가격 |
| `recent_x_data.csv` | 펀더멘털 변수 데이터 |

---

## 7. 주요 클래스/함수 참조

### 7.1 그래프 관련

| 파일 | 클래스/함수 | 설명 |
|------|------------|------|
| trading_graph.py | `MarketAgentsGraph` | 메인 오케스트레이터 |
| setup.py | `GraphSetup` | 그래프 노드/엣지 설정 |
| propagation.py | `Propagator` | 상태 초기화 및 전파 |
| conditional_logic.py | `ConditionalLogic` | 분기 조건 로직 |
| signal_processing.py | `SignalProcessor` | 최종 시그널 추출 |

### 7.2 에이전트 생성 함수

| 함수 | 반환 | 용도 |
|------|------|------|
| `create_market_analyst()` | node function | 시장 분석 노드 |
| `create_news_analyst()` | node function | 뉴스 분석 노드 |
| `create_social_media_analyst()` | node function | 소셜 분석 노드 |
| `create_fundamentals_analyst()` | node function | 펀더멘털 분석 노드 |
| `create_bull_researcher()` | node function | 강세 연구 노드 |
| `create_bear_researcher()` | node function | 약세 연구 노드 |
| `create_trader()` | node function | 트레이딩 노드 |
| `create_risky_debator()` | node function | 공격적 리스크 노드 |
| `create_safe_debator()` | node function | 보수적 리스크 노드 |
| `create_neutral_debator()` | node function | 중립적 리스크 노드 |
| `create_research_manager()` | node function | 연구 관리 노드 |
| `create_risk_manager()` | node function | 리스크 관리 노드 |

---

## 8. 사용 예시

```python
from marketagents.graph.trading_graph import MarketAgentsGraph
from marketagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# 설정 복사 및 수정
config = DEFAULT_CONFIG.copy()

# 그래프 초기화
ma = MarketAgentsGraph(debug=False, config=config)

# 예측 실행
target_date = "2025-12-05"
final_state, decision = ma.propagate("Brent crude oil price", target_date)

print("[DECISION]", decision)  # BUY, SELL, or HOLD
```

---

## 9. 출력 및 로깅

### 9.1 로그 파일 구조

```
eval_results/
└── {ticker}/
    └── MarketAgentsStrategy_logs/
        └── full_states_log_{trade_date}.json
```

### 9.2 로그 내용

```json
{
  "{trade_date}": {
    "company_of_interest": "...",
    "trade_date": "...",
    "market_report": "...",
    "sentiment_report": "...",
    "news_report": "...",
    "fundamentals_report": "...",
    "investment_plan": "...",
    "investment_debate_state": {
      "bull_history": "...",
      "bear_history": "..."
    },
    "trader_investment_plan": "...",
    "final_trade_decision": "...",
    "risk_debate_state": {
      "risky_history": "...",
      "safe_history": "...",
      "neutral_history": "..."
    }
  }
}
```

---

## 10. 의존성

### 10.1 주요 패키지

- `langchain-openai`: OpenAI LLM 연동
- `langchain-anthropic`: Anthropic LLM 연동
- `langchain-google-genai`: Google LLM 연동
- `langgraph`: 워크플로우 그래프
- `chromadb`: 벡터 데이터베이스 (메모리)
- `yfinance`: Yahoo Finance 데이터
- `pandas`: 데이터 처리
- `openai`: OpenAI API 클라이언트

### 10.2 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키
- `ANTHROPIC_API_KEY`: Anthropic API 키 (선택)
- `GOOGLE_API_KEY`: Google API 키 (선택)

---

## 11. 확장 포인트

### 11.1 새 분석가 추가

1. `agents/analysts/` 에 새 파일 생성
2. `create_xxx_analyst()` 함수 구현
3. `agents/__init__.py`에 export 추가
4. `setup.py`의 `setup_graph()`에 노드 추가

### 11.2 새 데이터 소스 추가

1. `dataflows/`에 유틸리티 함수 추가
2. `dataflows/interface.py`에 인터페이스 함수 추가
3. `agents/utils/agent_utils.py`의 `Toolkit`에 도구 메서드 추가

### 11.3 토론 라운드 조정

```python
config = DEFAULT_CONFIG.copy()
config["max_debate_rounds"] = 3      # Bull-Bear 토론 3라운드
config["max_risk_discuss_rounds"] = 2 # 리스크 토론 2라운드
```

---

## 12. 업데이트 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-30 | 1.0 | 초기 분석 문서 작성 |

---

*이 문서는 코드베이스 분석을 기반으로 자동 생성되었습니다. 코드 변경 시 업데이트가 필요합니다.*
