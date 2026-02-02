from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from datetime import datetime, timedelta
import pandas as pd


def create_fundamentals_analyst(llm, toolkit):

    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        # recent_variable_data = pd.read_csv('marketagents/agents/analysts/analyst_data/raw_data.csv').set_index('Date').to_string()
        recent_variable_data = pd.read_csv('marketagents/data/recent_x_data.csv').set_index('date').to_string()
        if toolkit.config["online_tools"]:
            tools = [
                # toolkit.get_fundamentals_data_online,
                # toolkit.get_economic_indicators_online,
            ]
        else:
            tools = [
                # toolkit.get_YFin_data,
                # toolkit.get_fundamentals_data,
            ]

        system_message = (
            """You are a fundamentals analyst specializing in Brent crude oil markets. Your primary role is to analyze recent variable data and create a comprehensive weekly storyline for the recent 1 month period.

            **CRITICAL REPORTING STANDARDS**:
            
            1. **Variable Selection & Quantification**:
            - MANDATORY: All key variables MUST include week-over-week (w/w) percentage change
            - Format: VARIABLE_NAME ↑/↓ +/-X% → current_value (ex. GPRD ↓ -21% → 151.6)
            - Only highlight variables with significant w/w changes (typically >5% for most metrics)
            - All percentage changes and current values must be shown for variables that moved > 5% w/w
            - Always specify the exact time period being compared

            2. **Week Coverage & Structure**:
            - SKIP the first week (no prior week for comparison)
            - Report EXACTLY 4 weeks (weeks 2, 3, 4, 5 of the dataset)
            - **Week Definition**: Count backwards from the last date in 5 business day increments to define each week (since only business days are included in data)
            - For cross-week periods (e.g., 7/18→8/15), explicitly state the date range
            - Each week period must be clearly defined with start-end dates

            3. **Data Consistency Requirements**:
            - Narrative MUST align with indicator movements
            - Example of WRONG approach: Describing "Asian refining margin weakness" while DUBSINR rises (3.27→4.39) indicates margin improvement
            - Example of CORRECT approach: If DUBSINR increases, describe "improving Asian refining margins" or "strengthening crack spreads"
            - Verify directional consistency between all numerical data and qualitative descriptions

            4. **Market Context**: Consider fundamental factors affecting crude oil prices including:
            - Supply/demand dynamics
            - Geopolitical events (GPRD index movements)
            - Economic indicators
            - Refining margins and crack spreads
            - Seasonal patterns
            - OPEC decisions
            - Currency movements

            **Analysis Framework**:
            - **Week-over-Week Analysis**: Calculate precise w/w percentage changes for all variables
            - **Trend Identification**: Distinguish between temporary fluctuations and sustained trends
            - **Fundamental Drivers**: Connect price movements to underlying fundamental factors
            - **Consistency Check**: Ensure all narratives match the directional movement of indicators

            **Variable Description Requirements**:
            - **MANDATORY**: All variables must include descriptive parentheses based on the reference table
            - **Format**: VARIABLE_NAME (descriptive explanation) ↑/↓ +/-X% → value
            - **Examples**: 
              • WTLM1UC (WTI–Brent 스프레드) ↓ -5.2% → 1.85
              • GPRD_THREAT (지정학적 리스크 지수) ↑ +12.3% → 156.2
              • D-AASFA00 (VLCC 운임지수) ↓ -8.7% → 44.7
            - **Compression Rule**: If description is too long, compress to key terms (max 3-4 words in parentheses)
            - **Korean Priority**: Use Korean descriptions from the reference table when available

            **Output Format - Markdown Table Structure Example (Fixed format)**
            
            **Quality Control Checklist**:
            ✓ All percentage changes and current values are shown for variables that moved > 5 % w/w
            ✓ Narratives match indicator directions
            ✓ Four weeks (Weeks 2-5) covered; first week excluded
            ✓ Date ranges, w/w metrics, and analysis fully aligned

            Focus on actionable insights that help traders understand the fundamental backdrop driving Brent crude oil price movements."""
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
                    """ For your reference, the current date is {current_date}. We are analyzing {ticker}. 

                    Recent Variable Data:
                    {recent_variable_data}

                    #### ■ **핵심변수 목록**
                    | 변수명                   | 설명                                                                          |
                    |:-------------------------|:------------------------------------------------------------------------------|
                    | NBRNCSF                  | Brent Crude Oil, NC 계약, Short 포지션, Futures 기준                          |
                    | USO                      | 미국 원유 펀드(USO), WTI 단기 가격 변동을 추종하는 ETF                        |
                    | WRPEXUS2_4WEEK_AVG       | 4주 평균 총 석유제품 수출량 (천 배럴/일)                                      |
                    | HOc1                     | 난방유 선물                                                                   |
                    | NBRTRSC                  | Brent Crude Oil, Total Return 계약, Short 포지션, 현금 기준                   |
                    | D-PCAAT00                | 두바이 원유(M1)                                                               |
                    | HOc1-CLc1                | 난방유(HO) 크랙(선물 기준)                                                    |
                    | .OVX                     | 원유 변동성 지수                                                              |
                    | D-PCAAQ00                | 브렌트유 M1 (Platts 평가)                                                     |
                    | NBRNCLF                  | Brent Crude Oil, NC 계약, Long 포지션, Futures 기준                           |
                    | RBc1-CLc1                | RBOB 가솔린 크랙 (선물 기준)                                                  |
                    | WCESTP21                 | 미국 중서부(PADD 2) 원유 재고 (전략비축유 제외, 천 배럴)                      |
                    | LLCC.01-LLCC.02          | Brent 1st/2nd(Intermonth Spread)                                              |
                    | NBRTRLC                  | Brent Crude Oil, Total Return 계약, Long 포지션, 현금 기준                    |
                    | D-PCACG00                | WTI M1 (Platts 평가)                                                          |
                    | WTTEXUS2                 | 미국의 원유 및 석유제품 주간 수출량 (천 배럴/일)                              |
                    | WTLM1UC                  | WTI-Brent 스프레드(USD/배럴)(근월물, ICE, 17:30 UK기준)                       |
                    | LLCSWLF                  | ICE 브렌트유, 스왑 딜러, Long 포지션, 선물 기준                               |
                    | LLCMMSF                  | ICE 브렌트유, 자산운용사(Managed Money), Short 포지션, 선물 기준              |
                    | WCEIMP42                 | 미국 로키산맥(PADD 4) 지역의 상업용 원유 수입량 (전략비축유 제외, 천 배럴/일) |
                    | W_EPC0_SKA_NUS_MBBL      | 알래스카에서 선박으로 수송 중인 미국 원유 재고량 (천 배럴)                    |
                    | WTTSTUS1                 | 미국의 원유 및 석유제품 주간 최종 재고량 (천 배럴)                            |
                    | NBRPMLF                  | Brent Crude Oil, PMP 계약, Long 포지션, Futures 기준                          |
                    | NBRSWLF                  | Brent Crude Oil, SD 계약, Long 포지션, Futures 기준                           |
                    | USIPENERP                | 미국 전체 에너지 생산량                                                       |
                    | NBRSWSC                  | Brent Crude Oil, SD 계약, Short 포지션, 현금 기준                             |
                    | NBRMMLF                  | Brent Crude Oil, MM 계약, Long 포지션, Futures 기준                           |
                    | WCRIMUS2                 | 미국의 원유 일일 수입량 (천 배럴/일)                                          |
                    | D-AASFA00                | VLCC 운임지수(WS)                                                             |
                    | NBRORLF                  | Brent Crude Oil, OR 계약, Long 포지션, Futures 기준                           |
                    | LLCPMLC                  | ICE 브렌트유, 생산자/상인, Long 포지션, 현금 기준                             |
                    | LLCSWXF                  | ICE 브렌트유, 스왑 딜러, 스프레드 포지션, 선물 기준                           |
                    | NBRORLC                  | Brent Crude Oil, OR 계약, Long 포지션, 현금 기준                              |
                    | EER_EPD2DC_PF4_Y05LA_DPG | 로스앤젤레스 CARB 인증 초저유황 디젤 현물가격 (달러/갤런)                     |

                    Create a comprehensive Markdown table analyzing the last 4-5 weeks with the following format:

                    | Week Period (2025) | Key Variables (w/w changes) | Fundamental Storyline | Market Implications |
                    |--------------------|-----------------------------|-----------------------|---------------------|
                    | Jul 25 → Aug 1 | • VARIABLE1 (변수명 설명) ↑ +X% → value <br>• VARIABLE2 (변수명 설명) ↓ -Y% → value <br>• VARIABLE3 (변수명 설명) ↑ +Z% → value | [Detailed analysis consistent with data] | [Market outlook] |
                    
                    (ex.)
                    | Week Period (2025) | Key Variables (w/w changes) | Fundamental Storyline | Market Implications |
                    |--------------------|-----------------------------|-----------------------|---------------------|
                    | Jul 23 → Jul 29 | • WTLM1UC (WTI–Brent 스프레드) ↓ -11.2% → 1.91 <br>• D-AASFA00 (VLCC 운임지수) ↓ -22.4% → 3.34 <br>• GPRD_THREAT (지정학적 리스크) ↑ +6.5% → 156.2 | Asian refining margin weakness and Brent backwardation easing spread physical bearish sentiment. Despite OPEC production cut reconfirmation, fundamental weakness signals persist. | Crack spread weakness signals downside risk warning; geopolitical tensions remain elevated supporting short-term premium outlook. |

                    **⚠️ MANDATORY**: Sort weekly periods (Week Period) chronologically (oldest date → most recent date)

                    Provide detailed analysis for each week, focusing on variables that showed the most significant changes. Include percentage calculations and explain the fundamental drivers behind each week's performance. Do not leave any cells empty or marked as "TBD". Exactly repeat previously defined **Quality Control Checklist** at the end of the report to ensure all requirements are met.""",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(recent_variable_data=recent_variable_data)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
