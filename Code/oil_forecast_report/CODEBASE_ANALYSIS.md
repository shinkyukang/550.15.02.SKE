# Oil Forecast Report - 코드베이스 분석

## 1. 개요

이 프로젝트는 **Brent 원유 가격 예측 및 투자 의사결정**을 위한 멀티 에이전트 시스템입니다. LangGraph를 기반으로 여러 AI 에이전트가 협업하여 시장 분석, 투자 토론, 리스크 평가를 수행하고 최종 거래 결정(BUY/SELL/HOLD)을 도출합니다.

### 핵심 특징
- **멀티 에이전트 아키텍처**: 다양한 전문 에이전트들이 협업
- **토론 기반 의사결정**: Bull/Bear 연구원 간 토론, 리스크 분석가 간 토론
- **메모리 기반 학습**: 과거 유사 상황에서의 교훈을 활용
- **하이브리드 데이터 소스**: 로컬 CSV 파일 + 실시간 온라인 데이터 수집

---

## 2. 프로젝트 구조

```
oil_forecast_report/
├── main.py                          # 진입점
├── pyproject.toml                   # 프로젝트 설정 및 의존성
├── .env.example                     # 환경변수 템플릿
├── eval_results/                    # 평가 결과 저장
└── marketagents/
    ├── default_config.py            # 기본 설정
    ├── data/                        # ⚠️ 입력 데이터 (필수)
    │   ├── AA-OIL_BRENT.csv         # Brent 원유 일별 가격
    │   └── recent_x_data.csv        # 펀더멘털 변수 데이터
    ├── agents/                      # 에이전트 정의
    │   ├── __init__.py              # 에이전트 모듈 export
    │   ├── analysts/                # 분석가 에이전트
    │   │   ├── market_analyst.py    # 시장 분석가 (AA-OIL_BRENT.csv 사용)
    │   │   ├── news_analyst.py      # 뉴스 분석가
    │   │   ├── social_media_analyst.py  # 소셜 미디어 분석가
    │   │   └── fundamentals_analyst.py  # 펀더멘털 분석가 (recent_x_data.csv 사용)
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
    │       ├── agent_utils.py       # 도구 및 유틸리티 (Toolkit 클래스)
    │       └── memory.py            # 메모리 시스템
    ├── dataflows/                   # 데이터 처리
    │   ├── interface.py             # 데이터 인터페이스 (외부 API 호출)
    │   ├── config.py                # 데이터 설정 (전역 config 관리)
    │   ├── yfin_utils.py            # Yahoo Finance 유틸리티
    │   ├── googlenews_utils.py      # Google News 유틸리티
    │   ├── reddit_utils.py          # Reddit 유틸리티 (현재 비활성화)
    │   └── utils.py                 # 일반 유틸리티
    └── graph/                       # 그래프 워크플로우
        ├── __init__.py
        ├── trading_graph.py         # 메인 그래프 클래스 (MarketAgentsGraph)
        ├── setup.py                 # 그래프 설정 (노드/엣지 정의)
        ├── propagation.py           # 상태 전파 (초기 상태 생성)
        ├── conditional_logic.py     # 조건부 로직 (토론 라운드 제어)
        ├── signal_processing.py     # 시그널 처리 (BUY/SELL/HOLD 추출)
        └── prompts/                 # 프롬프트 템플릿
            ├── introduction.txt
            ├── main_body.txt
            └── conclusion.txt
```

---

## 3. ⚠️ 입력 데이터 요구사항 (중요)

### 3.1 필수 입력 데이터 파일

시스템 실행을 위해 **2개의 CSV 파일**이 반드시 필요합니다. 이 파일들은 `marketagents/data/` 디렉토리에 위치해야 합니다.

#### 1) `AA-OIL_BRENT.csv` - Brent 원유 가격 데이터

| 항목 | 내용 |
|------|------|
| **사용처** | `market_analyst.py:13` |
| **용도** | 시장 분석가가 기술적 지표 계산에 사용 |
| **사용량** | 최근 250일 데이터 (`.iloc[-250:]`) |
| **컬럼** | `TRADEDATE`, `LLCC.01` (가격) |
| **데이터 범위** | 2008-01-01 ~ target_date |

```python
# market_analyst.py에서 사용
recent_price_data = pd.read_csv('marketagents/data/AA-OIL_BRENT.csv').iloc[-250:].set_index('TRADEDATE').to_string()
```

#### 2) `recent_x_data.csv` - 펀더멘털 변수 데이터

| 항목 | 내용 |
|------|------|
| **사용처** | `fundamentals_analyst.py:14` |
| **용도** | 펀더멘털 분석가가 시장 지표 분석에 사용 |
| **컬럼 수** | 200+ 개 변수 |
| **주요 변수** | 포지셔닝(NBRNCLF, NBRNCSF), 재고(WCESTUS1), 스프레드(WTLM1UC), VLCC 운임(D-AASFA00), 지정학적 리스크(GPRD) 등 |

```python
# fundamentals_analyst.py에서 사용
recent_variable_data = pd.read_csv('marketagents/data/recent_x_data.csv').set_index('date').to_string()
```

### 3.2 데이터 현행화 요구사항

> **⚠️ 중요**: `target_date`를 변경하여 실행하려면 반드시 해당 날짜까지의 데이터가 CSV 파일에 포함되어 있어야 합니다.

| 시나리오 | 필요 조치 |
|---------|----------|
| 새로운 날짜로 예측 | 두 CSV 파일에 해당 날짜까지 데이터 추가 필요 |
| 과거 날짜로 백테스트 | 해당 기간 데이터가 포함되어 있으면 실행 가능 |
| 데이터 없이 실행 | 분석가가 오래된/부정확한 데이터로 분석 수행 |

**현재 데이터 기준일**: 2025-12-05 (main.py의 target_date와 일치)

---

## 4. 아키텍처 및 워크플로우

### 4.1 전체 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT                                          │
│        Company Name + Trade Date + CSV 데이터 파일 (2개)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DATA ANALYSIS                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │   Market     │ │   Social     │ │    News      │ │ Fundamentals │    │
│  │   Analyst    │ │   Analyst    │ │   Analyst    │ │   Analyst    │    │
│  │ (CSV 사용)   │ │ (온라인)     │ │ (온라인)     │ │ (CSV 사용)   │    │
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

### 4.2 LangGraph 상태 머신

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

## 5. 핵심 컴포넌트 상세

### 5.1 MarketAgentsGraph (trading_graph.py)

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
- 다중 LLM 제공자 지원 (OpenAI, Anthropic, Google, Ollama, OpenRouter)
- Deep thinking LLM (o3)과 Quick thinking LLM (gpt-4.1) 구분
- 5개의 독립적인 메모리 시스템

### 5.2 상태 정의 (agent_states.py)

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

### 5.3 분석가 에이전트 (analysts/)

#### Market Analyst
- **역할**: 기술적 지표 분석
- **LLM**: `deep_thinking_llm` (o3)
- **데이터 소스**: `marketagents/data/AA-OIL_BRENT.csv` (최근 250일 가격 데이터)
- **분석 지표**: SMA (50, 200), EMA (10), MACD, RSI, Bollinger Bands, ATR, VWMA
- **출력**: 8개 지표를 포함한 마크다운 테이블

#### News Analyst
- **역할**: 글로벌 뉴스 및 거시경제 분석
- **LLM**: `quick_thinking_llm` (gpt-4.1)
- **도구**: `get_global_news_openai`, `get_google_news`
- **출력 형식**: 날짜, 이벤트, Net Impact (%), 근거, 소스 테이블

#### Social Media Analyst
- **역할**: 금융 웹사이트에서 소셜 센티먼트 수집
- **LLM**: `quick_thinking_llm` (gpt-4.1)
- **대상 소스**: wealthtrend.net, spglobal.com, oilprice.com 등 8개 사이트
- **출력 형식**: Net Sentiment (%) 스코어링 (-100% ~ +100%)

#### Fundamentals Analyst
- **역할**: 펀더멘털 변수 분석
- **LLM**: `deep_thinking_llm` (o3)
- **데이터 소스**: `marketagents/data/recent_x_data.csv`
- **분석 항목**: 포지셔닝 데이터, 재고, 스프레드, 운임지수 등 40+ 변수
- **출력 형식**: 주간 변화율(w/w %) 포함 4주 분석 테이블

### 5.4 연구원 에이전트 (researchers/)

#### Bull Researcher
- **역할**: 투자 찬성 논거 제시
- **LLM**: `quick_thinking_llm`
- **초점**: 성장 잠재력, 경쟁 우위, 긍정적 지표
- **특징**: 과거 유사 상황 메모리 활용

#### Bear Researcher
- **역할**: 투자 반대 논거 제시
- **LLM**: `quick_thinking_llm`
- **초점**: 리스크, 구조적 문제, 부정적 지표
- **특징**: Bull Researcher와 토론 형식으로 상호작용

### 5.5 리스크 관리 에이전트 (risk_mgmt/)

| 에이전트 | 역할 | 관점 | LLM |
|---------|------|------|-----|
| Risky Analyst | 고위험/고수익 옹호 | 공격적 투자 전략 | quick_thinking_llm |
| Safe Analyst | 자산 보호 우선 | 보수적/방어적 전략 | quick_thinking_llm |
| Neutral Analyst | 균형 잡힌 시각 | 양측 비판 및 중재 | quick_thinking_llm |

### 5.6 관리자 에이전트 (managers/)

#### Research Manager
- **LLM**: `deep_thinking_llm`
- Bull/Bear 토론 평가
- 투자 계획 수립 (Buy/Sell/Hold)
- 과거 실수에서 학습

#### Risk Manager
- **LLM**: `deep_thinking_llm`
- 3자 리스크 토론 평가
- 최종 거래 결정 도출
- 트레이더 계획 수정 및 확정

### 5.7 에이전트별 LLM 할당 요약

| 에이전트 | LLM 타입 | 기본 모델 |
|---------|----------|----------|
| Market Analyst | deep_thinking | o3 |
| Social Media Analyst | quick_thinking | gpt-4.1 |
| News Analyst | quick_thinking | gpt-4.1 |
| Fundamentals Analyst | deep_thinking | o3 |
| Bull Researcher | quick_thinking | gpt-4.1 |
| Bear Researcher | quick_thinking | gpt-4.1 |
| Research Manager | deep_thinking | o3 |
| Trader | quick_thinking | gpt-4.1 |
| Risky/Safe/Neutral Analyst | quick_thinking | gpt-4.1 |
| Risk Manager | deep_thinking | o3 |

### 5.8 메모리 시스템 (memory.py)

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

## 6. 설정 및 구성

### 6.1 기본 설정 (default_config.py)

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

### 6.2 지원 LLM 제공자

| 제공자 | Deep Think | Quick Think |
|--------|-----------|-------------|
| OpenAI | o3 | gpt-4.1 |
| Anthropic | (configurable) | (configurable) |
| Google | Gemini | Gemini |
| Ollama | (local) | (local) |
| OpenRouter | (proxy) | (proxy) |

---

## 7. 데이터 플로우

### 7.1 데이터 소스 유형

시스템은 **하이브리드 방식**으로 데이터를 수집합니다:

```
┌──────────────────────────────────────────────────────────────┐
│                      데이터 소스                              │
├──────────────────────────────┬───────────────────────────────┤
│      로컬 CSV 파일 (필수)     │     온라인 API (실시간)        │
├──────────────────────────────┼───────────────────────────────┤
│ • AA-OIL_BRENT.csv           │ • Yahoo Finance              │
│   → Market Analyst           │   → (도구로 사용 가능)         │
│                              │                               │
│ • recent_x_data.csv          │ • Google News                │
│   → Fundamentals Analyst     │   → News Analyst             │
│                              │                               │
│                              │ • OpenAI Web Search          │
│                              │   → Social/News Analyst      │
└──────────────────────────────┴───────────────────────────────┘
```

### 7.2 로컬 데이터 소스 상세

| 파일 | 사용 에이전트 | 코드 위치 | 용도 |
|------|-------------|----------|------|
| `AA-OIL_BRENT.csv` | Market Analyst | `market_analyst.py:13` | 기술적 지표 계산용 가격 데이터 |
| `recent_x_data.csv` | Fundamentals Analyst | `fundamentals_analyst.py:14` | 펀더멘털 변수 분석 |

### 7.3 온라인 데이터 소스 (활성화된 도구)

| 소스 | 도구 함수 | 용도 | 사용 에이전트 |
|------|----------|------|-------------|
| Yahoo Finance | `get_YFin_data_online()` | 실시간 주가 데이터 | (사용 가능하나 현재 비활성화) |
| Google News | `get_google_news()` | 뉴스 검색 | News Analyst |
| OpenAI Web Search | `get_global_news_openai()` | 글로벌/거시경제 뉴스 | News Analyst |
| OpenAI Web Search | `get_stock_news_openai()` | 종목별 소셜 센티먼트 | Social Media Analyst |

### 7.4 비활성화된 도구 (코드에 존재하나 주석 처리됨)

| 도구 | 용도 | 상태 |
|------|------|------|
| `get_reddit_news` | Reddit 글로벌 뉴스 | 주석 처리 |
| `get_reddit_stock_info` | Reddit 종목 뉴스 | 주석 처리 |
| `get_finnhub_news` | Finnhub 뉴스 | 주석 처리 |
| `get_finnhub_company_insider_*` | 내부자 거래 정보 | 주석 처리 |
| `get_simfin_*` | 재무제표 데이터 | 주석 처리 |
| `get_stockstats_*` | 기술적 지표 | 주석 처리 |

---

## 8. 실행 방법 및 주의사항

### 8.1 사전 요구사항

1. **Python 버전**: 3.10 이상
2. **필수 API 키**: OpenAI API 키
3. **필수 데이터 파일**: `AA-OIL_BRENT.csv`, `recent_x_data.csv`

### 8.2 설치 및 환경 설정

```bash
# 1. 프로젝트 디렉토리로 이동
cd oil_forecast_report

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. 의존성 설치
pip install -e .

# 4. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 입력
```

### 8.3 실행 전 체크리스트

> **⚠️ 중요**: 실행 전 반드시 확인하세요!

| 항목 | 확인 사항 |
|------|----------|
| **1. 데이터 현행화** | `target_date`까지 두 CSV 파일에 데이터가 있는지 확인 |
| **2. 날짜 설정** | `main.py`의 `target_date`가 데이터 범위 내인지 확인 |
| **3. API 키** | `.env` 파일에 `OPENAI_API_KEY` 설정 |
| **4. 데이터 경로** | CSV 파일이 `marketagents/data/` 디렉토리에 있는지 확인 |

### 8.4 실행 예시

```python
from marketagents.graph.trading_graph import MarketAgentsGraph
from marketagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# 설정 복사 및 수정
config = DEFAULT_CONFIG.copy()

# 그래프 초기화
ma = MarketAgentsGraph(debug=False, config=config)

# ⚠️ target_date는 CSV 데이터가 있는 날짜로 설정해야 함
target_date = "2025-12-05"  # 현재 데이터 기준일
final_state, decision = ma.propagate("Brent crude oil price", target_date)

print("[DECISION]", decision)  # BUY, SELL, or HOLD
```

### 8.5 새로운 날짜로 실행하기

새로운 날짜로 예측하려면:

1. **데이터 업데이트**:
   ```
   marketagents/data/AA-OIL_BRENT.csv     → 새 날짜까지 가격 데이터 추가
   marketagents/data/recent_x_data.csv   → 새 날짜까지 변수 데이터 추가
   ```

2. **main.py 수정**:
   ```python
   target_date = "2026-01-15"  # 새로운 날짜로 변경
   ```

3. **실행**:
   ```bash
   python main.py
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
- `python-dotenv`: 환경변수 관리
- `beautifulsoup4`: 웹 스크래핑

### 10.2 환경 변수 (.env)

| 변수명 | 필수 여부 | 용도 |
|--------|----------|------|
| `OPENAI_API_KEY` | **필수** | OpenAI API 인증 |
| `LANGSMITH_API_KEY` | 선택 | LangSmith 추적 |
| `LANGSMITH_PROJECT` | 선택 | LangSmith 프로젝트명 |
| `ANTHROPIC_API_KEY` | 선택 | Anthropic LLM 사용 시 |
| `GOOGLE_API_KEY` | 선택 | Google LLM 사용 시 |

---

## 11. 주요 클래스/함수 참조

### 11.1 그래프 관련

| 파일 | 클래스/함수 | 설명 |
|------|------------|------|
| trading_graph.py | `MarketAgentsGraph` | 메인 오케스트레이터 |
| setup.py | `GraphSetup` | 그래프 노드/엣지 설정 |
| propagation.py | `Propagator` | 상태 초기화 및 전파 |
| conditional_logic.py | `ConditionalLogic` | 분기 조건 로직 |
| signal_processing.py | `SignalProcessor` | 최종 시그널 추출 |

### 11.2 에이전트 생성 함수

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

## 12. 확장 포인트

### 12.1 새 분석가 추가

1. `agents/analysts/` 에 새 파일 생성
2. `create_xxx_analyst()` 함수 구현
3. `agents/__init__.py`에 export 추가
4. `setup.py`의 `setup_graph()`에 노드 추가

### 12.2 새 데이터 소스 추가

1. `dataflows/`에 유틸리티 함수 추가
2. `dataflows/interface.py`에 인터페이스 함수 추가
3. `agents/utils/agent_utils.py`의 `Toolkit`에 도구 메서드 추가

### 12.3 토론 라운드 조정

```python
config = DEFAULT_CONFIG.copy()
config["max_debate_rounds"] = 3      # Bull-Bear 토론 3라운드
config["max_risk_discuss_rounds"] = 2 # 리스크 토론 2라운드
```

---

## 13. 트러블슈팅

### 13.1 일반적인 오류

| 오류 | 원인 | 해결 방법 |
|------|------|----------|
| `FileNotFoundError: AA-OIL_BRENT.csv` | 데이터 파일 누락 | `marketagents/data/` 디렉토리에 파일 확인 |
| `OPENAI_API_KEY not found` | 환경변수 미설정 | `.env` 파일에 API 키 설정 |
| 오래된 분석 결과 | CSV 데이터가 target_date보다 과거 | 두 CSV 파일 데이터 현행화 |
| `RecursionLimit` | 토론 라운드 초과 | `max_recur_limit` 값 증가 |

### 13.2 데이터 검증 방법

```python
import pandas as pd

# AA-OIL_BRENT.csv 확인
df_price = pd.read_csv('marketagents/data/AA-OIL_BRENT.csv')
print(f"가격 데이터 범위: {df_price['TRADEDATE'].min()} ~ {df_price['TRADEDATE'].max()}")

# recent_x_data.csv 확인
df_vars = pd.read_csv('marketagents/data/recent_x_data.csv')
print(f"변수 데이터 범위: {df_vars['date'].min()} ~ {df_vars['date'].max()}")
```

---

## 14. 업데이트 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-30 | 1.0 | 초기 분석 문서 작성 |
| 2026-02-05 | 1.1 | 입력 데이터 요구사항 섹션 추가, 데이터 현행화 주의사항 추가, 에이전트별 LLM 할당 정보 추가, 활성화/비활성화 도구 구분, 트러블슈팅 섹션 추가 |

---

*이 문서는 코드베이스 분석을 기반으로 작성되었습니다. 코드 변경 시 업데이트가 필요합니다.*
