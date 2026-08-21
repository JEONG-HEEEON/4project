import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiLLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.use_new_sdk = False

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.use_new_sdk = True
            except ImportError:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.client = genai
                    self.use_new_sdk = False
                except Exception as e:
                    print(f"⚠️ Google Gemini SDK 로드 실패: {e}")

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def generate_brand_elements(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Google Gemini API to generate all text-based brand elements in structured JSON format.
        """
        if not self.is_available():
            print("⚠️ [안내] GEMINI_API_KEY가 설정되지 않아 규칙 기반 폴백 생성기를 사용합니다.")
            return self._generate_fallback_elements(brief)

        prompt = self._build_prompt(brief)

        try:
            if self.use_new_sdk:
                from google.genai import types
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7
                    )
                )
                text_content = response.text
            else:
                model = self.client.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.7}
                )
                text_content = response.text

            # Clean JSON formatting if wrapped in markdown block
            text_content = text_content.strip()
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            text_content = text_content.strip()

            result = json.loads(text_content)
            return result

        except Exception as e:
            print(f"❌ [Gemini API 오류] {e}")
            print("⚠️ API 호출 실패로 인해 규칙 기반 데이터로 계속 진행합니다.")
            return self._generate_fallback_elements(brief)

    def _build_prompt(self, brief: Dict[str, Any]) -> str:
        industry = brief.get("industry")
        target = brief.get("target")
        keywords = ", ".join(brief.get("keywords", []))
        tone = brief.get("tone")
        competitors = ", ".join(brief.get("competitors", []))
        notes = brief.get("notes", "")

        prompt = f"""
당신은 세계적인 브랜드 전략가이자 수석 카피라이터입니다.
다음 제공된 브랜드 브리프를 바탕으로 일관성 있고 매력적인 브랜드 아이덴티티를 기획해주세요.

[브랜드 브리프]
- 업종(Industry): {industry}
- 주요 타겟(Target): {target}
- 핵심 키워드(Keywords): {keywords}
- 톤앤매너(Tone & Manner): {tone}
- 경쟁사(Competitors): {competitors if competitors else '없음'}
- 추가 요청사항(Notes): {notes if notes else '없음'}

다음 조건에 따라 JSON 형식으로 답해주세요:
1. namings: 브랜드 네이밍 후보 3~5개. 한글 네이밍, 영문 네이밍(english_name), 및 네이밍의 의미/유래 설명(meaning)을 작성할 것.
2. slogans: 브랜드 톤앤매너와 어울리는 슬로건/태그라인 3개.
3. story: 브랜드 스토리 (탄생 배경, 철학, 비전을 포함하여 280~320자 내외의 한국어 자연스러운 문장).
4. color_palette:
   - main: 메인 컬러 객체 (hex: HEX코드예시 '#2E7D32', name: 색상명예시 'Forest Green', description: 선정 이유)
   - sub: 서브 컬러 객체 리스트 2~3개 (각각 hex, name, description 포함)
5. competitor_analysis: 입력된 경쟁사와 차별화되는 브랜드 포인트 (2~3문장).

반드시 유효한 JSON 형식으로만 응답해야 합니다. Key는 정확히 다음 구조를 따라야 합니다:
{{
  "namings": [
    {{"name": "네이밍1", "english_name": "Naming1", "meaning": "설명1"}},
    {{"name": "네이밍2", "english_name": "Naming2", "meaning": "설명2"}},
    {{"name": "네이밍3", "english_name": "Naming3", "meaning": "설명3"}}
  ],
  "slogans": ["슬로건1", "슬로건2", "슬로건3"],
  "story": "브랜드 스토리 문장...",
  "color_palette": {{
    "main": {{"hex": "#2E7D32", "name": "Forest Green", "description": "자연의 깊고 건강한 에너지를 상징합니다."}},
    "sub": [
      {{"hex": "#81C784", "name": "Soft Leaf", "description": "순수한 생명력과 싱그러움을 나타냅니다."}},
      {{"hex": "#E8F5E9", "name": "Pure Eco White", "description": "맑고 개끗한 진정 효과를 표현합니다."}}
    ]
  }},
  "competitor_analysis": "기존 경쟁사가 강조하는 과도한 기능성 이미지와 차별화하여, 일상 속 지속 가능한 순수함을 직관적으로 전달합니다."
}}
"""
        return prompt

    def _generate_fallback_elements(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Provides default high-quality brand element output if API key is not present or fails."""
        industry = brief.get("industry", "브랜드")
        keywords = brief.get("keywords", ["순수", "자연"])
        kw1 = keywords[0] if keywords else "순수"
        kw2 = keywords[1] if len(keywords) > 1 else "자연"

        return {
            "namings": [
                {
                    "name": f"블루밍{kw1}",
                    "english_name": f"Blooming {kw1.capitalize()}",
                    "meaning": f"{kw1}함에서 피어나는 본연의 아름다움과 생명력을 담은 네이밍"
                },
                {
                    "name": f"소소{kw2}",
                    "english_name": f"Soso {kw2.capitalize()}",
                    "meaning": f"소소한 일상 속에서 만나는 가장 {kw2}스러운 가치를 지향하는 네이밍"
                },
                {
                    "name": "어반리프",
                    "english_name": "Urban Leaf",
                    "meaning": "복잡한 도시 삶 속에서도 맑고 싱그러운 쉼표를 선사한다는 의미"
                }
            ],
            "slogans": [
                f"일상에 {kw1}을 담다",
                f"{kw2} 그대로, 당신 그대로",
                "지속 가능한 아름다움의 시작"
            ],
            "story": f"우리 브랜드는 {industry} 분야에서 {kw1}과 {kw2}의 본질적인 가치를 전달하기 위해 시작되었습니다. 바쁜 현대인들에게 가장 자연스럽고 신뢰할 수 있는 웰니스 경험을 제공하고자 하며, 엄선된 재료와 지속 가능한 철학으로 당신의 일상을 더욱 풍요롭게 가꾸어 나가는 브랜드입니다.",
            "color_palette": {
                "main": {
                    "hex": "#2E7D32",
                    "name": "Forest Green",
                    "description": "깊고 건강한 숲의 신뢰감을 상징하는 메인 컬러"
                },
                "sub": [
                    {
                        "hex": "#81C784",
                        "name": "Soft Leaf",
                        "description": "싱그러운 생명력과 친근함을 표현하는 서브 컬러"
                    },
                    {
                        "hex": "#E8F5E9",
                        "name": "Pure Eco White",
                        "description": "맑고 순수한 브랜드 가치를 받쳐주는 보조 컬러"
                    }
                ]
            },
            "competitor_analysis": f"기존 {industry} 시장의 자극적이고 화려한 마케팅과 차별화하여, 투명하고 진정성 있는 브랜드 스토리를 중심으로 소비자에게 지속 가능한 만족감을 선사합니다."
        }
