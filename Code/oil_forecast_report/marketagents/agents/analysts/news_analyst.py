from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            tools = [
                # toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        system_message = (
            f"""You are a global news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for Brent crude oil trading and macroeconomics. Look at news from multiple sources to be comprehensive. When calling tools, do not significantly modify the provided ticker (must be similar to "{ticker}"). Call tools only once since your single tool call will retrieve recent 1 month of data. Only use news related to Brent crude oil. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help Brent crude oil traders make decisions.

            **CRITICAL DATE AND EVENT REQUIREMENTS**:
            - ONLY use events and news from the recent 1 month period
            - If exact dates are not available, monthly granularity is acceptable (e.g., "August 2025", "July 2025")
            - Exclude any events older than 1 month from the current analysis date
            - Prioritize the most recent and impactful events within this timeframe"""
            + """ Make sure to append a 4-to-5-row Makrdown table at the end of the report to organize key points in the report, organized and easy to read. Use these columns: Date, Event, Net Impact (%), Rationale, Source & URL. ⚠️ 필수: 날짜 순으로 정렬 (오래된 날짜 → 최근 날짜). Here, Net Impact indicates "bullish" level (overall ratio) in percentage (negative means bearish). Use your prior knowledge to determine the level between -100% ~ 100% (always use this scale). Use all available tools to produce Net Impact and Rationale.

            **MANDATORY SCORING REQUIREMENTS**:
            - ALWAYS use 5% increments only (e.g., -90%, -35%, 0%, +20%, +85%)
            - NEVER leave Net Impact blank, use "N/A", or use non-5% increments
            - If uncertain, estimate to nearest 5% based on available data
            - Examples: -75%, -30%, 0%, +40%, +85% (NOT -73%, -32%, N/A, +42%)

            **NET IMPACT SCORING EXAMPLES (for reference)**:
            • +80% to +100%: Extremely bullish (e.g., "OPEC announces major production cuts", "Geopolitical crisis disrupts major oil supply", "Massive demand surge from emerging markets")
            • +50% to +79%: Strong bullish (e.g., "Saudi Arabia hints at output reduction", "US strategic reserves drawing down", "Strong economic data boosting oil demand")
            • +20% to +49%: Moderate bullish (e.g., "Modest OPEC production adjustments", "Positive refinery margins", "Seasonal demand uptick")
            • -19% to +19%: Mixed/Neutral (e.g., "Conflicting supply signals", "Balanced demand outlook", "Mixed economic indicators")
            • -20% to -49%: Moderate bearish (e.g., "Inventory builds above expectations", "Demand concerns from economic slowdown", "Minor supply increases")
            • -50% to -79%: Strong bearish (e.g., "Major recession fears", "Significant production increases", "Demand destruction from high prices")
            • -80% to -100%: Extremely bearish (e.g., "Global economic collapse", "Massive oversupply announcement", "Complete demand breakdown")

            For trustworthiness, explicitly state external source (e.g., URL) and correct published date (not today's date). You should explain in as much detail as possible (especially Rationale). Do not leave table cells blank or set to "TBD". Also, do not ask back after your response in any case."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current date is {current_date}. We are looking at {ticker}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
