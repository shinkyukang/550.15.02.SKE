from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage


class BaseWriter:
    """
    모든 리포트 섹션 작성을 담당하는 통합 Writer 클래스
    """
    
    def __init__(self, llm, prompts: Dict[str, str], section_name: str):
        """
        Writer 초기화
        
        Args:
            llm: 언어 모델 인스턴스
            prompts: 프롬프트 템플릿 딕셔너리
            section_name: 섹션 이름
        """
        self.llm = llm
        self.prompts = prompts
        self.section_name = section_name
    
    def generate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        콘텐츠 생성
        
        Args:
            state: 분석 결과가 포함된 상태 딕셔너리
            
        Returns:
            생성된 콘텐츠가 추가된 상태 딕셔너리
        """
        # 프롬프트 템플릿 가져오기
        prompt_template = self.prompts.get(self.section_name, "")
        if not prompt_template:
            raise ValueError(f"{self.section_name} 프롬프트를 찾을 수 없습니다.")
        
        # 상태에서 필요한 정보 추출
        market_data = self._extract_market_data(state)
        
        # 프롬프트 포맷팅
        formatted_prompt = prompt_template.format(**market_data)
        
        # LLM 호출
        content = self._call_llm(formatted_prompt)
        
        # 결과 상태 생성
        return self._create_result_state(state, content)
    
    def _extract_market_data(self, state: Dict[str, Any]) -> Dict[str, str]:
        """상태에서 시장 데이터 추출"""
        market_data = {
            "trade_date": state.get("trade_date", ""),
            "company_of_interest": state.get("company_of_interest", ""),
            "market_report": state.get("market_report", ""),
            "sentiment_report": state.get("sentiment_report", ""),
            "news_report": state.get("news_report", ""),
            "fundamentals_report": state.get("fundamentals_report", ""),
            "investment_plan": state.get("investment_plan", ""),
            "final_trade_decision": state.get("final_trade_decision", "")
        }
        
        return market_data
    
    def _call_llm(self, formatted_prompt: str) -> str:
        """LLM 호출"""
        messages = [
            SystemMessage(content="당신은 전문 금융 리포트 작성자입니다."),
            HumanMessage(content=formatted_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _create_result_state(self, original_state: Dict[str, Any], content: str) -> Dict[str, Any]:
        """결과 상태 딕셔너리 생성"""
        new_state = original_state.copy()
        new_state[self.section_name] = content
        new_state["sender"] = f"{self.section_name}_writer"
        
        # 생성 메타데이터 추가
        new_state["generation_metadata"] = {
            "section": self.section_name,
            "word_count": len(content.split()),
            "character_count": len(content),
            "model_used": getattr(self.llm, 'model_name', 'unknown'),
            "timestamp": original_state.get("trade_date", "")
        }
        
        return new_state
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """콘텐츠 검증 (섹션별 로직 적용)"""
        word_count = len(content.split())
        char_count = len(content)
        
        validation_result = {
            "is_valid": True,
            "issues": [],
            "word_count": word_count,
            "character_count": char_count,
            "estimated_reading_time": round(word_count / 200, 1)
        }
        
        # 섹션별 검증 로직
        if self.section_name == "introduction":
            return self._validate_introduction(content, validation_result)
        elif self.section_name in ["main_body", "conclusion"]:
            return self._validate_general_section(content, validation_result)
        else:
            # 기본 검증
            return self._validate_basic(content, validation_result)
    
    def _validate_introduction(self, content: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """서론 특화 검증"""
        word_count = base_result["word_count"]
        
        # 길이 검증
        if word_count < 150:
            base_result["issues"].append("서론이 너무 짧습니다 (150단어 미만)")
            base_result["is_valid"] = False
        elif word_count > 300:
            base_result["issues"].append("서론이 너무 깁니다 (300단어 초과)")
            base_result["is_valid"] = False
        
        # 구조 검증
        required_elements = [
            ("분석", "분석 대상 언급"),
            ("시장", "시장 상황 언급"),
            ("리포트", "리포트 구성 안내")
        ]
        
        for keyword, description in required_elements:
            if keyword not in content:
                base_result["issues"].append(f"{description}이 누락되었을 수 있습니다")
        
        # 전문성 검증
        financial_terms = [
            "가격", "시장", "거래", "투자", "분석", "전망", "리스크", 
            "수익", "변동", "추세", "지표", "데이터"
        ]
        
        found_terms = sum(1 for term in financial_terms if term in content)
        if found_terms < 3:
            base_result["issues"].append("금융 전문 용어가 부족할 수 있습니다")
        
        base_result["financial_term_count"] = found_terms
        return base_result
    
    def _validate_general_section(self, content: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """일반 섹션 검증"""
        word_count = base_result["word_count"]
        
        # 섹션별 길이 검증
        if self.section_name == "conclusion":
            # 결론 섹션: 최대 250단어
            if word_count < 100:
                base_result["issues"].append("결론이 너무 짧습니다 (100단어 미만)")
                base_result["is_valid"] = False
            elif word_count > 250:
                base_result["issues"].append("결론이 너무 깁니다 (250단어 초과)")
                base_result["is_valid"] = False
        else:
            # 기타 섹션 (본론 등): 기존 로직 유지
            if word_count < 300:
                base_result["issues"].append("내용이 너무 짧습니다 (300단어 미만)")
                base_result["is_valid"] = False
            elif word_count > 1200:
                base_result["issues"].append("내용이 너무 깁니다 (1200단어 초과)")
        
        return base_result
    
    def _validate_basic(self, content: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """기본 검증"""
        word_count = base_result["word_count"]
        
        if word_count < 100:
            base_result["issues"].append("내용이 너무 짧습니다")
            base_result["is_valid"] = False
        
        return base_result


def format_complete_report_output(complete_report: str, metadata: Dict[str, Any] = None, validation: Dict[str, Any] = None) -> str:
    """
    전체 리포트를 마크다운 형식으로 포맷팅
    
    Args:
        complete_report: 생성된 전체 리포트 텍스트
        metadata: 메타데이터 딕셔너리
        validation: 검증 결과 딕셔너리
    
    Returns:
        포맷팅된 마크다운 텍스트
    """
    # 메타데이터 헤더 추가
    if metadata:
        header = "<!-- 리포트 메타데이터 -->\n"
        header += f"<!-- 생성일: {metadata.get('generation_date', 'N/A')} -->\n"
        header += f"<!-- 분석 대상: {metadata.get('company_of_interest', 'N/A')} -->\n"
        header += f"<!-- 분석 날짜: {metadata.get('trade_date', 'N/A')} -->\n"
        
        if validation:
            header += f"<!-- 총 단어 수: {validation.get('total_word_count', 'N/A')} -->\n"
            header += f"<!-- 예상 읽기 시간: {validation.get('estimated_reading_time', 'N/A')}분 -->\n"
            header += f"<!-- 생성 섹션: {', '.join(metadata.get('sections_generated', []))} -->\n"
        
        header += "\n"
        
        return header + complete_report
    
    return complete_report 