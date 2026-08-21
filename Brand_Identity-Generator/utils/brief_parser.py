import json
import os
from typing import Dict, Any

class BriefValidationError(Exception):
    """Raised when a brand brief JSON is invalid or missing required fields."""
    pass

def load_brief(file_path: str) -> Dict[str, Any]:
    """
    Loads and validates a brand brief JSON file.

    Required fields:
    - industry (업종)
    - target (타겟)
    - keywords (키워드: list or str)

    Optional fields:
    - tone (톤앤매너)
    - competitors (경쟁사: list or str)
    - notes (추가 요청사항)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"브리프 파일을 찾을 수 없습니다: '{file_path}'")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise BriefValidationError(f"JSON 파일 형식이 올바르지 않습니다: {e}")

    if not isinstance(data, dict):
        raise BriefValidationError("브리프 파일은 JSON 객체(dict) 형식이어야 합니다.")

    # Validate required fields
    required_fields = ["industry", "target", "keywords"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        raise BriefValidationError(f"필수 입력 항목이 누락되었습니다: {', '.join(missing)}")

    # Standardize data format
    keywords = data["keywords"]
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    competitors = data.get("competitors", [])
    if isinstance(competitors, str):
        competitors = [c.strip() for c in competitors.split(",") if c.strip()]

    brief = {
        "industry": str(data["industry"]).strip(),
        "target": str(data["target"]).strip(),
        "keywords": keywords,
        "tone": str(data.get("tone", "세련되고 전문적인")).strip(),
        "competitors": competitors,
        "notes": str(data.get("notes", "")).strip()
    }

    return brief
