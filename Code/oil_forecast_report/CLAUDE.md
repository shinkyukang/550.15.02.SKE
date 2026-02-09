# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered Brent crude oil price forecast report generator using a multi-agent LangGraph system. 12 specialized agents collaborate through analysis, debate, and risk assessment phases to produce a BUY/SELL/HOLD trading decision. Built with LangChain + LangGraph, Python 3.10+.

## Commands

```bash
# Install dependencies (using uv)
uv sync

# Install dependencies (using pip)
pip install -e .

# Run the full pipeline
python main.py
```

There are no test or lint commands configured for this project.

## Environment Setup

Copy `.env.example` to `.env` and set:
- `OPENAI_API_KEY` (required) — used for LLMs and embeddings
- `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` (optional) — for LangSmith tracing
- `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` (optional) — for alternative LLM providers

## Architecture

### Entry Point

`main.py` creates a `MarketAgentsGraph`, calls `propagate(company_name, target_date)`, and prints the final BUY/SELL/HOLD decision.

### Package Structure: `marketagents/`

**`graph/`** — LangGraph workflow orchestration
- `trading_graph.py`: `MarketAgentsGraph` — main orchestrator. Initializes LLMs (two tiers: deep-thinking and quick-thinking), 5 ChromaDB semantic memories, tool nodes, and compiles the LangGraph.
- `setup.py`: `GraphSetup` — builds the `StateGraph` by wiring analyst → researcher → trader → risk nodes with conditional edges.
- `propagation.py`: Creates initial `AgentState` with company/date and sub-states (`InvestDebateState`, `RiskDebateState`).
- `conditional_logic.py`: Controls looping — analysts loop until tools finish, debate loops for `max_debate_rounds`, risk discussion loops for `max_risk_discuss_rounds`.
- `signal_processing.py`: Extracts "BUY"/"SELL"/"HOLD" from the final decision text via LLM.
- `writing_graph.py`: Separate graph for generating formatted reports from prompt templates in `prompts/`.

**`agents/`** — Agent implementations (each exports a `create_*` factory function)
- `analysts/`: 4 analysts — `market_analyst` (deep-think, technical indicators from CSV), `fundamentals_analyst` (deep-think, 200+ variables from CSV), `news_analyst` (quick-think, Google News + OpenAI web search), `social_media_analyst` (quick-think, financial website sentiment)
- `researchers/`: `bull_researcher` and `bear_researcher` — debate opposing investment theses using semantic memory
- `managers/`: `research_manager` (deep-think, judges bull/bear debate → investment plan), `risk_manager` (deep-think, final trading decision)
- `risk_mgmt/`: 3 risk debaters — `aggresive_debator`, `conservative_debator`, `neutral_debator`
- `trader/`: Implements trading strategy from the investment plan
- `writers/`: `base_writer` for report generation
- `utils/agent_states.py`: `AgentState` (TypedDict with `MessagesState`) — the shared state flowing through the graph. Contains report fields, debate sub-states, and the final decision.
- `utils/agent_utils.py`: `Toolkit` class — wraps data collection tools (Yahoo Finance, Google News, OpenAI web search). Many tools are commented out (Reddit, Finnhub, SimFin).
- `utils/memory.py`: `FinancialSituationMemory` — ChromaDB-backed semantic memory with OpenAI embeddings for recalling similar past market situations.

**`dataflows/`** — External data collection and processing
- `interface.py`: Core API interface (Yahoo Finance, Google News, web scraping)
- `config.py`: Global config management
- `yfin_utils.py`, `googlenews_utils.py`, `reddit_utils.py`, `utils.py`: Data source utilities

**`data/`** — Input CSV files (must be updated for each run)
- `AA-OIL_BRENT.csv`: Historical Brent crude prices (TRADEDATE, LLCC.01 columns). Market Analyst uses last 250 days (`.iloc[-250:]`) at `market_analyst.py:13`.
- `recent_x_data.csv`: 200+ fundamental variables (positioning, inventory, spreads, shipping, geopolitical risk, etc.). Fundamentals Analyst reads all rows at `fundamentals_analyst.py:14`.

**Data currency requirement**: Both CSV files **must contain data up to `target_date`**. If data is stale, analysts will produce analysis based on outdated information. To validate:
```python
import pandas as pd
pd.read_csv('marketagents/data/AA-OIL_BRENT.csv')['TRADEDATE'].max()
pd.read_csv('marketagents/data/recent_x_data.csv')['date'].max()
```

### Analyst Output Formats

| Agent | Output | Format |
|-------|--------|--------|
| Market Analyst | 8 technical indicators (SMA 50/200, EMA 10, MACD, RSI, Bollinger Bands, ATR, VWMA) | Markdown table |
| News Analyst | Global/macro events | Date / Event / Net Impact (%) / Source table |
| Social Media Analyst | Sentiment from 8 financial websites | Net Sentiment score (-100% ~ +100%) |
| Fundamentals Analyst | 40+ variables (positioning, inventory, spreads, shipping, etc.) | 4-week w/w % change table |

### Pipeline Flow

```
Phase 1: ANALYSIS (4 analysts run sequentially, each with tool-calling loops)
  Market → [Msg Clear] → Social → [Msg Clear] → News → [Msg Clear] → Fundamentals → [Msg Clear]
    ↓
Phase 2: DEBATE (Bull ↔ Bear researchers alternate for max_debate_rounds)
  → Research Manager produces investment plan
    ↓
Phase 3: TRADING (Trader creates trading strategy)
    ↓
Phase 4: RISK (Risky ↔ Safe ↔ Neutral debaters cycle for max_risk_discuss_rounds)
  → Risk Manager produces final trade decision
    ↓
Phase 5: SIGNAL (LLM extracts BUY/SELL/HOLD)
```

Each analyst phase has a `Msg Clear` node between phases that clears message history from state. This is necessary for Anthropic LLM compatibility and prevents context pollution between independent analysts.

### LLM Tiers

Configured in `default_config.py`:
- **Deep-thinking** (`o3` by default): Market Analyst, Fundamentals Analyst, Research Manager, Risk Manager
- **Quick-thinking** (`gpt-4.1` by default): News Analyst, Social Media Analyst, Bull/Bear Researchers, Trader, Risk Debaters

Supports OpenAI, Anthropic, Google Gemini, Ollama, and OpenRouter via `llm_provider` config.

### Key Config (`default_config.py`)

- `max_debate_rounds`: Bull/Bear debate iterations (default: 2)
- `max_risk_discuss_rounds`: Risk debate iterations (default: 1)
- `online_tools`: Enable/disable live data collection (default: True)

### Output

Results are logged as JSON to `eval_results/{ticker}/MarketAgentsStrategy_logs/full_states_log_{trade_date}.json`, containing all agent reports, debate histories, and the final decision.

## Extending the System

### Adding a New Agent

1. Create the agent file under the appropriate `agents/` subdirectory
2. Implement a `create_*` factory function that takes an LLM (and optionally toolkit/memory)
3. Export from `agents/__init__.py`
4. Wire into the graph in `graph/setup.py` by adding a node and edges

### Adding a New Data Source

1. Create utility functions in `dataflows/` (e.g., `new_source_utils.py`)
2. Add interface functions in `dataflows/interface.py`
3. Add a tool method to the `Toolkit` class in `agents/utils/agent_utils.py`
4. Register the tool in the appropriate `ToolNode` in `trading_graph.py:_create_tool_nodes()`

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError: AA-OIL_BRENT.csv` | Missing data file | Ensure CSVs exist in `marketagents/data/` |
| `OPENAI_API_KEY not found` | Env var not set | Set key in `.env` file |
| Stale/inaccurate analysis | CSV data older than `target_date` | Update both CSV files with data through `target_date` |
| `RecursionLimit` | Too many debate rounds | Increase `max_recur_limit` in config |
