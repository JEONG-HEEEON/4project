# 🎨 브랜드 아이덴티티 생성기 (Brand Identity Generator)

Google Gemini API (LLM 및 Imagen API)를 활용하여 브랜드 브리프(업종, 타겟, 키워드 등)를 바탕으로 **네이밍, 슬로건, 브랜드 스토리, 컬러 팔레트, 로고 시안**까지 자동으로 생성하는 Python CLI 프로그램입니다.

---

## 🌟 주요 기능

1. **브랜드 브리프 파싱 (`brief.json`)**:
   - 필수 필드: 업종(`industry`), 타겟(`target`), 키워드(`keywords`)
   - 선택 필드: 톤앤매너(`tone`), 경쟁사(`competitors`), 추가 요청사항(`notes`)
2. **AI 기반 브랜드 아이덴티티 기획 (Google Gemini API)**:
   - 브랜드 네이밍 후보 3~5개 (한글 + 영문 다국어 네이밍 지원 및 의미/유래 제공)
   - 톤앤매너에 맞춘 슬로건/태그라인 3개
   - 탄생 배경, 철학, 비전을 담은 브랜드 스토리 (~300자)
   - 메인 컬러 (1개) 및 서브 컬러 (2~3개) HEX 코드 및 설명
   - 경쟁사 차별화 포인트 제안 (보너스 기능)
3. **컬러 팔레트 시각화 (PNG)**:
   - Matplotlib를 활용하여 컬러 블록, HEX 코드, 색상명, 설명이 포함된 카드 이미지 생성 (`color_palette.png`)
4. **로고 시안 생성 (PNG)**:
   - Gemini Imagen API (또는 그래픽 엔진)를 이용해 2~3개의 로고 시안 이미지 생성 (`logo_01.png`, `logo_02.png`)
5. **결과물 자동 저장**:
   - 모든 텍스트 결과물을 `./output/brand_result.json`으로 저장
   - 생성된 이미지를 개별 PNG 파일로 저장
6. **안전한 에러 처리 및 API 키 관리**:
   - `.env` 파일 및 환경 변수로 `GEMINI_API_KEY` 관리
   - API 키 미설정 또는 실패 시에도 예외 없이 예시 폴백 데이터로 정상 동작

---

## 📁 프로젝트 구조

```
Brand_Identity-Generator/
├── brand_generator.py       # 메인 CLI 실행 스크립트
├── brief.json               # 입력 브랜드 브리프 예시 파일
├── .env.example             # API 키 설정 템플릿
├── README.md                # 사용 설명서
├── output/                  # 생성 결과물 저장 폴더
│   ├── brand_result.json    # 통합 텍스트 결과 (JSON)
│   ├── color_palette.png    # 컬러 팔레트 시각화 이미지
│   ├── logo_01.png          # 로고 시안 1
│   └── logo_02.png          # 로고 시안 2
├── services/
│   ├── llm_service.py       # Gemini LLM 기반 텍스트 아이덴티티 생성 서비스
│   ├── image_service.py     # 로고 시안 이미지 생성 서비스
│   └── visualizer.py        # Matplotlib 기반 컬러 팔레트 시각화
└── utils/
    └── brief_parser.py      # 브리프 JSON 검증 및 파싱 모듈
```

---

## 🚀 사용 방법

### 1. 개발 환경 설정 및 패키지 설치

Python 3.10 이상이 필요합니다.

```bash
pip install -r requirements.txt
# 또는 주요 패키지 설치:
pip install google-genai matplotlib pillow python-dotenv
```

### 2. Gemini API 키 설정

1. `.env.example` 파일을 복사하여 `.env` 파일을 만듭니다.
2. `GEMINI_API_KEY`에 본인의 Google Gemini API 키를 작성합니다.

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

> 💡 **참고**: API 키를 설정하지 않거나 잘못 입력된 경우에도 안내 메시지와 함께 스마트 폴백 생성기가 작동되어 프로그램이 멈추지 않고 완료됩니다.

### 3. 브리프 작성 (`brief.json`)

```json
{
  "industry": "친환경 화장품",
  "target": "20-30대 여성",
  "keywords": ["자연", "순수", "건강"],
  "tone": "따뜻하고 신뢰감 있는",
  "competitors": ["이니스프리", "아로마티카"],
  "notes": "지속 가능한 패키징과 유기농 성분을 강조하는 비건 화장품 브랜드"
}
```

### 4. 프로그램 실행

#### 대화형 (Interactive) 실행
```bash
python brand_generator.py
```
실행 후 안내 메시지에 따라 브리프 파일 경로(`brief.json`)와 출력 폴더 경로(`./output`)를 입력합니다.

#### 인자 (Arguments) 지정 실행
```bash
python brand_generator.py --brief brief.json --output ./output
```

---

## 🎯 실행 결과 예시

```text
🎨 AI 브랜드 아이덴티티 생성기

[1/5] 브랜드 네이밍 생성 중...
  - 블루밍자연 (Blooming Nature): 자연함에서 피어나는 본연의 아름다움과 생명력을 담은 네이밍
  - 소소순수 (Soso Pure): 소소한 일상 속에서 만나는 가장 순수한 가치를 지향하는 네이밍
  - 어반리프 (Urban Leaf): 복잡한 도시 삶 속에서도 맑고 싱그러운 쉼표를 선사한다는 의미
[2/5] 슬로건 생성 중...
  - "일상에 자연을 담다"
  - "순수 그대로, 당신 그대로"
  - "지속 가능한 아름다움의 시작"
[3/5] 브랜드 스토리 생성 중...
  - 스토리 생성 완료 (287자)
[4/5] 컬러 팔레트 생성 중...
  - 메인: #2E7D32 (Forest Green)
  - 서브: #81C784, #E8F5E9
  - 저장: ./output/color_palette.png
[5/5] 로고 시안 생성 중...
  - 저장: ./output/logo_01.png
  - 저장: ./output/logo_02.png

✅ 완료! ./output/ 폴더를 확인하세요.
```

---

## 🎓 핵심 과제 학습 포인트

1. **브랜드 파이프라인 이해**: 브리프 입력부터 텍스트/이미지 기반 브랜딩 통합 파이프라인 자동화.
2. **LLM + Image API 조합**: Google Gemini LLM API로 구조화된 JSON 데이터 생성 후, 이를 프롬프트로 가공하여 로고 이미지를 생성하는 멀티모달 파이프라인 구현.
3. **데이터 시각화**: Matplotlib 및 Pillow를 활용하여 색상 HEX 코드를 실제 카드 형태 PNG로 시각화.
4. **예외 처리 및 안전성**: API 키 부재, 네트워크 오류, 파일 경로 에러 등 다채로운 예외 상황에 대한 명확한 메시지 및 폴백 대응.
