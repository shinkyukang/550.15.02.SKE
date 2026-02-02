from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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

        prompt = f"""You are a Bear Analyst making the case against investing in Brent crude oil. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Structural Challenges: Assess downside risks specific to Brent crude, including potential oversupply in North Sea production, fluctuating European refining margins, OPEC+ policy misalignment, and volatility from geopolitical tensions affecting Brent's benchmark status. Examine how these factors could impair Brent-linked trading performance in both short and long-term contexts.
- Competitive Vulnerabilities: Highlight weaknesses such as reduced market share in Brent futures relative to WTI or other benchmarks, lagging innovation in Brent-specific trading models, or declining liquidity in deferred Brent contracts. Explore how these vulnerabilities could limit profitability and strategic positioning in the Brent market.
- Adverse Indicators: Use evidence from Brent forward curve structures (contango/backwardation), Brent futures positioning data, regional inventory reports, and negative macroeconomic or geopolitical headlines impacting North Sea supply and European demand. Leverage these signals to reinforce a bearish Brent thesis.
- Countering Bullish Narratives: Rigorously analyze optimistic claims regarding Brent demand recovery, supply discipline, or geopolitical risk premiums. Utilize quantitative data to expose weaknesses in bullish scenarios and demonstrate why downside pressures on Brent are more structurally significant.
- Engaged Analytical Tone: Craft the analysis as a direct debate with bullish Brent analysts. Engage their arguments point-by-point with empirical data and scenario analysis, presenting a clear and assertive bearish stance on Brent crude oil trading.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the Brent crude oil. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
