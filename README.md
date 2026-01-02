# CiteAgent - Automated Citation Assistant for Overleaf

CiteAgent는 Overleaf에서 작성 중인 LaTeX 논문에 자동으로 적절한 인용을 추가해주는 AI 기반 도구입니다.

**주요 기능:**
- 🤖 Upstage Solar Pro 2 LLM을 사용한 지능적인 인용 필요성 판단
- 📚 Semantic Scholar API를 통한 실시간 논문 검색
- 🔍 자동으로 가장 관련성 높은 논문 선택
- ✍️ LaTeX 문서에 `\citep{}` 태그 자동 삽입
- 📝 BibTeX 엔트리 자동 생성 및 추가
- 🌐 Selenium을 통한 Overleaf 브라우저 자동화
- 🦁 **Chrome과 Safari 모두 지원!**

**빠르게 시작하기:** [QUICKSTART.md](QUICKSTART.md)를 참고하세요 (5분 소요)
**Safari 사용자:** [SAFARI_SETUP.md](SAFARI_SETUP.md)를 참고하세요
**SSH 서버 사용자:** [SSH_SERVER_GUIDE.md](SSH_SERVER_GUIDE.md)를 참고하세요 (중요!)

## 목차

- [설치 방법](#설치-방법)
- [설정](#설정)
- [사용 방법](#사용-방법)
  - [1. Chrome 디버깅 모드 실행](#1-chrome-디버깅-모드-실행)
  - [2. Interactive 모드](#2-interactive-모드-권장)
  - [3. Full Document 모드](#3-full-document-모드)
  - [4. File 모드](#4-file-모드)
- [작동 원리](#작동-원리)
- [문제 해결](#문제-해결)
- [고급 사용법](#고급-사용법)

## 설치 방법

### 1. 저장소 클론

```bash
cd /mnt/ddn/kyudan/citeAgent
```

### 2. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. ChromeDriver 설치

Selenium이 Chrome을 제어하려면 ChromeDriver가 필요합니다.

```bash
# webdriver-manager가 자동으로 설치하지만, 수동 설치도 가능:
# Mac (Homebrew)
brew install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Windows - https://chromedriver.chromium.org/downloads 에서 다운로드
```

## 설정

### 1. 설정 파일 생성

```bash
cp config.yaml.example config.yaml
```

### 2. API 키 설정

`config.yaml` 파일을 열고 Upstage API 키를 입력합니다:

```yaml
upstage:
  api_key: "your_actual_api_key_here"  # 여기에 실제 API 키 입력
  base_url: "https://api.upstage.ai/v1"
  model: "solar-pro2"
```

**Upstage API 키 발급 방법:**
1. [Upstage Console](https://console.upstage.ai/)에 접속
2. 회원가입 또는 로그인
3. API Keys 메뉴에서 새 키 생성
4. 생성된 키를 복사하여 `config.yaml`에 붙여넣기

**환경변수로도 설정 가능:**

```bash
export UPSTAGE_API_KEY="your_api_key_here"
```

### 3. (선택사항) 설정 커스터마이징

```yaml
agent:
  max_papers_per_search: 5      # 검색당 최대 논문 수
  min_citation_count: 10        # 최소 인용 횟수 필터
  temperature: 0.3              # LLM 생성 온도 (0.0 ~ 1.0)

chrome:
  debug_port: 9222              # Chrome 디버깅 포트
  user_data_dir: "ChromeProfile"  # Chrome 프로필 디렉토리
```

## 사용 방법

### 1. Chrome 디버깅 모드 실행

CiteAgent가 Overleaf에 접속하려면 Chrome을 디버깅 모드로 실행해야 합니다.

**기존 Chrome 창을 모두 닫고** 다음 명령어를 실행하세요:

#### Mac:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/ChromeProfile"
```

#### Linux:
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/ChromeProfile"
```

#### Windows (PowerShell):
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="C:\ChromeProfile"
```

**그런 다음:**
1. 열린 Chrome에서 Overleaf (https://www.overleaf.com) 접속
2. 로그인 후 작업할 프로젝트 열기
3. 편집할 `.tex` 파일 선택

### 2. Interactive 모드 (권장)

텍스트를 선택하고 처리하는 대화형 모드입니다.

```bash
python main.py --interactive
```

**사용 순서:**
1. Overleaf 에디터에서 인용이 필요한 텍스트를 마우스로 드래그하여 선택
2. 터미널에서 Enter 키 입력
3. Agent가 자동으로 논문을 검색하고 인용 추가
4. 결과 확인 후 적용 여부 선택 (yes/no)
5. 적용하면 선택한 텍스트가 인용과 함께 교체되고, BibTeX가 `references.bib`에 자동 추가

**장점:**
- 안전함 (일부 텍스트만 처리)
- 실시간으로 결과 확인 가능
- 원치 않는 변경 방지

### 3. Full Document 모드

현재 열린 문서 전체를 한 번에 처리합니다.

```bash
# Overleaf에 직접 적용
python main.py --full-document

# 파일로 저장 (안전)
python main.py --full-document --output modified.tex
```

**주의사항:**
- 문서 전체가 변경될 수 있으므로 백업 권장
- 처리 시간이 길 수 있음 (문서 길이에 따라)
- 적용 전 반드시 결과 검토

### 4. File 모드

Overleaf 없이 로컬 `.tex` 파일을 처리합니다.

```bash
python main.py --file document.tex
```

출력:
- `document_cited.tex` - 인용이 추가된 문서
- `document_cited.bib` - BibTeX 엔트리들

**장점:**
- Overleaf 연결 불필요
- 오프라인 작업 가능
- 버전 관리 용이

## 작동 원리

```
┌─────────────────┐
│  Overleaf       │
│  (Chrome)       │
└────────┬────────┘
         │ Selenium
         ↓
┌─────────────────┐      ┌──────────────────┐
│ Overleaf        │─────→│  Citation Agent  │
│ Controller      │      │  (Solar Pro 2)   │
└─────────────────┘      └────────┬─────────┘
                                  │
                         Function Calling
                                  │
                    ┌─────────────┴────────────┐
                    ↓                          ↓
         ┌──────────────────┐      ┌──────────────────┐
         │  Paper Searcher  │      │  BibTeX Generator│
         │ (Semantic Scholar)│     └──────────────────┘
         └──────────────────┘
```

### 처리 과정:

1. **텍스트 분석**: LLM이 LaTeX 텍스트를 읽고 인용이 필요한 부분 식별
2. **논문 검색**: 식별된 주장/사실에 대해 Semantic Scholar API로 관련 논문 검색
3. **논문 선택**: 검색 결과에서 인용 횟수, 연도, 관련성을 고려하여 최적의 논문 선택
4. **BibTeX 생성**: 선택된 논문의 메타데이터로 BibTeX 엔트리 자동 생성
5. **텍스트 수정**: 적절한 위치에 `\citep{key}` 또는 `\citet{key}` 삽입
6. **적용**: Overleaf 에디터에 수정된 텍스트 반영, `.bib` 파일에 엔트리 추가

### LLM Function Calling

CiteAgent는 Upstage Solar Pro 2의 Function Calling 기능을 사용합니다:

- **search_paper**: 논문 검색 도구
- **get_bibtex**: BibTeX 엔트리 생성 도구

LLM이 스스로 필요한 도구를 호출하므로, 환각(hallucination) 없이 실제 존재하는 논문만 인용합니다.

## 문제 해결

### 1. "Could not connect to Overleaf" 에러

**원인**: Chrome이 디버깅 모드로 실행되지 않았거나, Overleaf가 열려있지 않음

**해결**:
- 모든 Chrome 창을 닫고 디버깅 모드로 재시작
- 포트 번호 확인 (`config.yaml`의 `chrome.debug_port`와 실행 명령어 일치 필요)
- Overleaf 프로젝트가 실제로 열려 있는지 확인

### 2. "Could not find ACE editor" 에러

**원인**: Overleaf 에디터가 로드되지 않았거나 UI가 변경됨

**해결**:
- 페이지 새로고침 후 재시도
- `.tex` 파일이 실제로 에디터에 열려있는지 확인
- 브라우저 콘솔에서 `ace.edit('editor')` 입력해보고 에러 확인

### 3. API 호출 에러

**원인**: API 키가 유효하지 않거나 요청 한도 초과

**해결**:
- API 키 확인: `config.yaml` 또는 환경변수
- Upstage Console에서 사용량 확인
- 네트워크 연결 확인

### 4. 논문 검색 결과 없음

**원인**: 검색 쿼리가 너무 구체적이거나 최소 인용 횟수 필터가 너무 높음

**해결**:
- `config.yaml`에서 `min_citation_count` 값 낮추기 (기본 10)
- 더 일반적인 텍스트로 시도
- Semantic Scholar API 상태 확인 (https://api.semanticscholar.org/)

### 5. BibTeX가 .bib 파일에 추가되지 않음

**원인**: Overleaf 파일 트리 구조 변경 또는 `.bib` 파일명 불일치

**해결**:
- 프로젝트에 `references.bib` 파일이 있는지 확인
- 터미널에 출력된 BibTeX 엔트리를 수동으로 복사하여 붙여넣기
- 다른 `.bib` 파일명을 사용하는 경우 코드 수정 필요

## 고급 사용법

### 환경변수로 API 키 관리

```bash
# .bashrc 또는 .zshrc에 추가
export UPSTAGE_API_KEY="up_xxxxxxxxxxxxx"

# 사용
python main.py --interactive
```

### 커스텀 설정 파일 사용

```bash
python main.py --config custom_config.yaml --interactive
```

### 특정 섹션만 처리

1. Overleaf에서 처리하고 싶은 섹션만 복사
2. 로컬 파일로 저장 (`section.tex`)
3. File 모드로 처리:
   ```bash
   python main.py --file section.tex
   ```
4. 결과를 Overleaf로 다시 복사

### Python 스크립트로 통합

```python
from src.citation_agent import CitationAgent
from src.config import Config

# 설정 로드
config = Config("config.yaml")
upstage_config = config.get_upstage_config()

# Agent 초기화
agent = CitationAgent(
    api_key=upstage_config["api_key"],
    model=upstage_config["model"]
)

# 텍스트 처리
text = "Transformers have revolutionized NLP."
modified, bibtex = agent.process_text(text)

print(modified)
print(bibtex)
```

## 프로젝트 구조

```
citeAgent/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # Python 의존성
├── config.yaml.example     # 설정 파일 예시
├── config.yaml            # 실제 설정 파일 (gitignore)
├── README.md              # 이 문서
├── .gitignore
└── src/
    ├── __init__.py
    ├── config.py          # 설정 관리
    ├── paper_search.py    # Semantic Scholar 연동
    ├── citation_agent.py  # LLM Agent 로직
    └── overleaf_controller.py  # Selenium Overleaf 제어
```

## 라이선스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!

## 참고 자료

- [Upstage API 문서](https://developers.upstage.ai/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [Selenium Python 문서](https://selenium-python.readthedocs.io/)
- [Overleaf](https://www.overleaf.com/)

## 주의사항

- 이 도구는 연구 보조 목적으로 제작되었습니다
- 생성된 인용은 반드시 검토하고 확인해야 합니다
- 부정확한 인용이나 저작권 문제에 대한 책임은 사용자에게 있습니다
- Overleaf의 자동 저장 기능으로 변경사항이 자동 저장되므로, 중요한 작업 전 백업을 권장합니다

---

**Made with ❤️ for researchers**
