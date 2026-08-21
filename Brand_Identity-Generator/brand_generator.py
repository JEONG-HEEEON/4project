#!/usr/bin/env python3
"""
AI 브랜드 아이덴티티 생성기 (Brand Identity Generator)
Gemini LLM API와 이미지 생성 API를 활용하여 브리프 기반 브랜드 아이덴티티 자동 생성
"""

import sys
import os
import json
import argparse
from typing import Dict, Any

# Windows 콘솔 표준 출력 인코딩 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from utils.brief_parser import load_brief, BriefValidationError
from services.llm_service import GeminiLLMService
from services.visualizer import visualize_color_palette
from services.image_service import GeminiImageService

def parse_args():
    parser = argparse.ArgumentParser(description="AI 브랜드 아이덴티티 생성기")
    parser.add_argument("-b", "--brief", type=str, help="브랜드 브리프 JSON 파일 경로")
    parser.add_argument("-o", "--output", type=str, default=None, help="결과물 저장 폴더 경로 (기본값: ./output)")
    return parser.parse_args()

def main():
    args = parse_args()

    print("\n🎨 AI 브랜드 아이덴티티 생성기\n")

    # 1. 브리프 파일 경로 입력받기
    brief_path = args.brief
    if not brief_path:
        try:
            brief_path = input("브리프 파일 경로를 입력하세요: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n프로그램을 종료합니다.")
            sys.exit(0)

    if not brief_path:
        print("❌ 브리프 파일 경로가 입력되지 않았습니다.")
        sys.exit(1)

    # 2. 출력 폴더 경로 입력받기
    output_dir = args.output
    if not output_dir:
        try:
            user_out = input("출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()
            output_dir = user_out if user_out else "./output"
        except (KeyboardInterrupt, EOFError):
            output_dir = "./output"

    os.makedirs(output_dir, exist_ok=True)

    # 3. 브리프 파싱 및 검증
    try:
        brief = load_brief(brief_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except BriefValidationError as e:
        print(f"❌ 브리프 검증 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        sys.exit(1)

    # 4. LLM 및 Image 서비스 초기화
    llm_service = GeminiLLMService()
    image_service = GeminiImageService()

    # 5. 브랜드 요소를 Gemini API로 생성
    print("\n[1/5] 브랜드 네이밍 생성 중...")
    generated_elements = llm_service.generate_brand_elements(brief)

    namings = generated_elements.get("namings", [])
    for n in namings:
        name_str = n.get('name', '')
        eng_str = n.get('english_name', '')
        meaning_str = n.get('meaning', '')
        display_name = f"{name_str} ({eng_str})" if eng_str else name_str
        print(f"  - {display_name}: {meaning_str}")

    print("[2/5] 슬로건 생성 중...")
    slogans = generated_elements.get("slogans", [])
    for s in slogans:
        print(f'  - "{s}"')

    print("[3/5] 브랜드 스토리 생성 중...")
    story = generated_elements.get("story", "")
    print(f"  - 스토리 생성 완료 ({len(story)}자)")

    print("[4/5] 컬러 팔레트 생성 중...")
    color_palette = generated_elements.get("color_palette", {})
    main_color = color_palette.get("main", {})
    sub_colors = color_palette.get("sub", [])

    main_hex = main_color.get("hex", "#2E7D32")
    main_name = main_color.get("name", "Main Color")
    print(f"  - 메인: {main_hex} ({main_name})")

    sub_hex_list = [s.get("hex", "#81C784") for s in sub_colors]
    print(f"  - 서브: {', '.join(sub_hex_list)}")

    palette_png_path = os.path.join(output_dir, "color_palette.png")
    try:
        visualize_color_palette(color_palette, palette_png_path)
        print(f"  - 저장: {palette_png_path}")
    except Exception as e:
        print(f"  ⚠️ 컬러 팔레트 시각화 경고: {e}")

    print("[5/5] 로고 시안 생성 중...")
    try:
        logo_paths = image_service.generate_logos(
            brand_info={
                "namings": namings,
                "industry": brief.get("industry"),
                "color_palette": color_palette
            },
            output_dir=output_dir,
            num_logos=2
        )
        for lp in logo_paths:
            print(f"  - 저장: {lp}")
    except Exception as e:
        print(f"  ⚠️ 로고 시안 생성 경고: {e}")

    # 6. 최종 결과 JSON 저장
    result_data = {
        "brief": brief,
        "brand_identity": {
            "namings": namings,
            "slogans": slogans,
            "story": story,
            "color_palette": color_palette,
            "competitor_analysis": generated_elements.get("competitor_analysis", "")
        },
        "files": {
            "color_palette_image": palette_png_path,
            "logo_images": logo_paths if 'logo_paths' in locals() else []
        }
    }

    result_json_path = os.path.join(output_dir, "brand_result.json")
    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료! {output_dir}/ 폴더를 확인하세요.\n")

if __name__ == "__main__":
    main()
