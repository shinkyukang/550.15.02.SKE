import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from marketagents.default_config import DEFAULT_CONFIG
from marketagents.agents.writers.base_writer import BaseWriter


class WritingGraph:
    """
    MarketAgents 결과물을 기반으로 위클리 리포트를 작성하는 클래스
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Writing Graph 초기화
        
        Args:
            config: 설정 딕셔너리. None이면 기본 설정 사용
        """
        self.config = config or DEFAULT_CONFIG
        self.llm = self._initialize_llm()
        self.prompts = self._load_prompts()
        
        # 🎯 통합된 Writer 에이전트들 초기화
        self.writers = self._initialize_writers()
    
    def _initialize_llm(self):
        """LLM 초기화"""
        provider = self.config.get("llm_provider", "openai")
        model = self.config.get("deep_think_llm", "gpt-4")
        
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=self.config.get("backend_url", "https://api.openai.com/v1")
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif provider == "google":
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _load_prompts(self) -> Dict[str, str]:
        """프롬프트 템플릿 파일에서 로드"""
        prompts_path = Path(__file__).parent / "prompts"
        prompts = {}
        
        if not prompts_path.exists():
            raise FileNotFoundError(
                f"프롬프트 디렉토리를 찾을 수 없습니다: {prompts_path}\n"
                f"프롬프트 파일들을 생성해주세요."
            )
        
        # 섹션별 프롬프트 파일 로드
        prompt_files = [f for f in prompts_path.glob("*.txt")]
        if not prompt_files:
            raise FileNotFoundError(
                f"프롬프트 파일(*.txt)을 찾을 수 없습니다: {prompts_path}\n"
                f"최소한 introduction.txt 파일이 필요합니다."
            )
        
        for prompt_file in prompt_files:
            section = prompt_file.stem
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        prompts[section] = content
            except Exception as e:
                print(f"❌ 프롬프트 파일 로드 실패: {prompt_file} - {e}")
        
        if not prompts:
            raise ValueError("유효한 프롬프트를 로드할 수 없습니다.")
        
        return prompts
    
    def _initialize_writers(self) -> Dict[str, BaseWriter]:
        """Writer 에이전트들 초기화 (모든 섹션이 동일한 BaseWriter 사용)"""
        writers = {}
        
        # 모든 섹션에 대해 BaseWriter 사용
        for section in self.prompts:
            writers[section] = BaseWriter(self.llm, self.prompts, section)
        
        return writers
    
    def load_market_data(self, file_path: str, date: str = None) -> Dict[str, Any]:
        """
        MarketAgents 결과 JSON 파일 로드
        
        Args:
            file_path: JSON 파일 경로
            date: 특정 날짜 (None이면 가장 최근 데이터)
            
        Returns:
            시장 데이터 딕셔너리
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if date:
            if date in data:
                return data[date]
            else:
                raise ValueError(f"Date {date} not found in data")
        else:
            # 가장 최근 날짜 데이터 반환
            latest_date = max(data.keys())
            return data[latest_date]
    
    def generate_section(self, section: str, market_data: Dict[str, Any]) -> str:
        """
        특정 섹션 생성
        
        Args:
            section: 섹션 이름
            market_data: MarketAgents 분석 결과
            
        Returns:
            생성된 섹션 텍스트
        """
        if section not in self.writers:
            raise ValueError(f"Unknown section: {section}. {section}.txt 파일이 필요합니다.")
        
        writer = self.writers[section]
        result_state = writer.generate(market_data)
        return result_state.get(section, "")
    
    def generate_section_with_metadata(self, section: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        메타데이터와 검증을 포함한 섹션 생성
        
        Args:
            section: 섹션 이름
            market_data: MarketAgents 분석 결과
            
        Returns:
            섹션, 메타데이터, 검증 결과가 포함된 딕셔너리
        """
        if section not in self.writers:
            raise ValueError(f"Unknown section: {section}. {section}.txt 파일이 필요합니다.")
        
        writer = self.writers[section]
        result_state = writer.generate(market_data)
        content = result_state.get(section, "")
        
        # 검증 수행
        validation = writer.validate_content(content)
        
        return {
            "content": content,
            "metadata": result_state.get("generation_metadata", {}),
            "validation": validation,
            "raw_state": result_state
        }
    
    def get_writer(self, section: str) -> BaseWriter:
        """특정 섹션의 Writer 반환"""
        if section not in self.writers:
            raise ValueError(f"Unknown section: {section}")
        return self.writers[section]
    
    def list_available_sections(self) -> list[str]:
        """사용 가능한 섹션 목록 반환"""
        return list(self.prompts.keys())
    
    def save_output(self, content: str, output_path: str, section: str = None, custom_filename: str = None):
        """
        생성된 콘텐츠 저장
        
        Args:
            content: 생성된 텍스트
            output_path: 저장 경로
            section: 섹션 이름 (파일명에 포함됨)
            custom_filename: 사용자 정의 파일명 (확장자 제외)
        """
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if custom_filename:
            # 사용자 정의 파일명 사용
            filename = f"{custom_filename}.md"
            full_path = output_dir / filename
        elif section:
            # 기존 방식: 섹션명 + 타임스탬프
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{section}_{timestamp}.md"
            full_path = output_dir / filename
        else:
            # 전체 경로 사용
            full_path = Path(output_path)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Content saved to: {full_path}")
        return str(full_path)
    
    def generate_complete_report(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전체 리포트 생성 (모든 섹션)
        
        Args:
            market_data: MarketAgents 분석 결과
            
        Returns:
            전체 리포트와 메타데이터가 포함된 딕셔너리
        """
        sections_order = ["introduction", "main_body", "conclusion"]
        available_sections = [s for s in sections_order if s in self.writers]
        
        if not available_sections:
            raise ValueError("생성 가능한 섹션이 없습니다. 프롬프트 파일을 확인해주세요.")
        
        results = {}
        total_word_count = 0
        total_character_count = 0
        all_issues = []
        
        print(f"전체 리포트 생성 중... (섹션: {', '.join(available_sections)})")
        
        for section in available_sections:
            print(f"  📝 {section} 생성 중...")
            try:
                result = self.generate_section_with_metadata(section, market_data)
                results[section] = result
                
                # 통계 누적
                total_word_count += result["validation"]["word_count"]
                total_character_count += result["validation"]["character_count"]
                all_issues.extend(result["validation"].get("issues", []))
                
                print(f"  ✅ {section} 완료 ({result['validation']['word_count']}단어)")
                
            except Exception as e:
                print(f"  ❌ {section} 생성 실패: {e}")
                results[section] = {
                    "content": f"[{section} 생성 실패: {str(e)}]",
                    "validation": {"word_count": 0, "character_count": 0, "issues": [str(e)]},
                    "metadata": {}
                }
        
        # 전체 리포트 조합
        complete_report = self._combine_sections(results, available_sections, market_data)
        
        # 전체 검증 결과
        overall_validation = {
            "is_valid": len(all_issues) == 0,
            "total_word_count": total_word_count,
            "total_character_count": total_character_count,
            "estimated_reading_time": round(total_word_count / 200, 1),
            "sections_count": len(available_sections),
            "issues": all_issues
        }
        
        return {
            "complete_report": complete_report,
            "sections": results,
            "validation": overall_validation,
            "metadata": {
                "generation_date": datetime.now().isoformat(),
                "trade_date": market_data.get("trade_date"),
                "company_of_interest": market_data.get("company_of_interest"),
                "sections_generated": available_sections
            }
        }
    
    def _combine_sections(self, results: Dict[str, Dict[str, Any]], sections_order: list, market_data: Dict[str, Any] = None) -> str:
        """섹션들을 하나의 완전한 리포트로 조합"""
        report_parts = []
        
        # 헤더 추가 - market_data 우선, 없으면 raw_state에서 가져오기
        trade_date = market_data.get("trade_date", "N/A")
        company = market_data.get("company_of_interest", "N/A")
        
        report_parts.append(f"# 유가 전망 리포트")
        report_parts.append(f"**분석 대상**: {company}")
        report_parts.append(f"**분석 날짜**: {trade_date}")
        report_parts.append(f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append("")
        
        # 기준가 정보 추가 (일정한 포맷)
        price_info = market_data.get("price_info", {})
        if price_info:
            report_parts.append("## 📊 주요 가격 정보")
            report_parts.append("")
            
            # 날짜에서 월/일 형식 추출
            target_date = price_info.get("target_date", "")
            if target_date:
                try:
                    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
                    formatted_date = f"{date_obj.month}/{date_obj.day}"
                except:
                    formatted_date = target_date
            else:
                formatted_date = "N/A"
            
            current_price = price_info.get("current_price")
            prev_4weeks_avg = price_info.get("prev_4weeks_avg")
            predicted_price = price_info.get("predicted_price")
            
            # 일정한 포맷으로 출력
            if current_price is not None and prev_4weeks_avg is not None:
                report_parts.append(f"- **금주 기준가**: {current_price} ({formatted_date}), **이전 4주 평균**: {prev_4weeks_avg}")
            elif current_price is not None:
                report_parts.append(f"- **금주 기준가**: {current_price} ({formatted_date})")
            
            if predicted_price is not None:
                report_parts.append(f"- **금주 예측가**: {predicted_price}")
            
            report_parts.append("")
        
        report_parts.append("---")
        report_parts.append("")
        
        # 각 섹션 추가
        section_titles = {
            "introduction": "## 1. 서론",
            "main_body": "## 2. 본론",
            "conclusion": "## 3. 결론"
        }
        
        for section in sections_order:
            if section in results:
                title = section_titles.get(section, f"## {section.title()}")
                content = results[section]["content"]
                
                report_parts.append(title)
                report_parts.append("")
                report_parts.append(content)
                report_parts.append("")
                report_parts.append("---")
                report_parts.append("")
        
        # 푸터 추가
        report_parts.append("*본 리포트는 AI 분석 시스템에 의해 생성된 정보 제공 목적의 자료이며, 투자 조언이 아닙니다.*")
        
        return "\n".join(report_parts) 