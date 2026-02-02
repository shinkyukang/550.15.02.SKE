from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""You are a Bull Analyst advocating for investing in the Brent crude oil. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Emphasize Brent crude's role as a key pricing benchmark for European and global markets and its strategic importance in global energy trade. Highlight demand recovery across Europe, the structural reliance on Brent-linked contracts, and the scalability of trading strategies designed to capture Brent's liquidity and price volatility. Incorporate revenue projections tied to widening Brent spreads and increased participation in derivatives markets.
- Competitive Advantages: Showcase Brent-specific strengths such as robust liquidity in international futures markets, strong linkage to physical North Sea cargoes, and seamless integration with global pricing mechanisms. Emphasize proprietary trading models built around Brent market dynamics, advanced risk management systems, and established relationships with counterparties active in Brent-focused trading hubs.
- Positive Indicators: Leverage evidence such as tightening European and global inventory levels, persistent backwardation in Brent futures, supportive positioning data, and bullish geopolitical or macroeconomic developments that reinforce Brent's premium. Validate the bullish thesis with performance metrics from Brent-oriented trading operations.
- Addressing Bearish Counterpoints: Directly engage with bearish narratives around potential oversupply or demand stagnation. Use data-driven analysis to demonstrate how OPEC+ supply discipline, strong refining margins, and Brent's benchmark status mitigate these risks. Show why structural and cyclical drivers are positioned to support Brent price appreciation over bearish scenarios.
- Engaged Analytical Tone: Frame the bullish thesis as an active dialogue with bearish Brent analysts. Counter their arguments point-by-point using empirical evidence and scenario analysis, reinforcing a conviction-based, optimistic outlook on Brent crude oil trading.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
