# CiteAgent - Project Summary

## 프로젝트 개요

CiteAgent는 Overleaf에서 작성 중인 LaTeX 논문에 자동으로 학술 논문 인용을 추가해주는 AI 기반 도구입니다.

**제작일**: 2026-01-02
**위치**: `/mnt/ddn/kyudan/citeAgent`

## 핵심 기능

✅ **완전히 작동하는 기능**:

1. **지능형 인용 판단**: Upstage Solar Pro 2 LLM이 어떤 문장에 인용이 필요한지 자동 판단
2. **실시간 논문 검색**: Semantic Scholar API를 통해 실제 학술 논문 검색
3. **자동 BibTeX 생성**: 검색된 논문의 메타데이터로 BibTeX 엔트리 자동 생성
4. **Overleaf 자동화**: Selenium으로 브라우저 제어, 텍스트 자동 교체
5. **3가지 실행 모드**: Interactive, Full Document, File 모드 지원

## 기술 스택

### Backend
- **언어**: Python 3.8+
- **LLM**: Upstage Solar Pro 2 (Function Calling)
- **검색 API**: Semantic Scholar Graph API
- **브라우저 자동화**: Selenium WebDriver
- **설정 관리**: PyYAML

### 아키텍처
```
User Input
    ↓
CLI Interface (main.py)
    ↓
Citation Agent (Solar Pro 2 + Function Calling)
    ↓
Paper Search (Semantic Scholar) + BibTeX Generator
    ↓
Overleaf Controller (Selenium + ACE Editor)
    ↓
Updated Document + References.bib
```

## 파일 구조

```
citeAgent/
├── README.md                   # 메인 문서 (설치, 설정, 사용법)
├── QUICKSTART.md               # 5분 빠른 시작 가이드
├── USAGE_EXAMPLES.md           # 상세 사용 예시
├── ARCHITECTURE.md             # 내부 구조 설명
├── PROJECT_SUMMARY.md          # 이 파일
│
├── main.py                     # 메인 실행 파일 (CLI)
├── test_agent.py              # 테스트 스크립트
├── verify_setup.py            # 환경 검증 스크립트
│
├── requirements.txt           # Python 의존성
├── config.yaml.example        # 설정 파일 예시
├── .env.example              # 환경변수 예시
├── .gitignore                # Git 제외 파일
│
├── start_chrome.sh           # Chrome 실행 스크립트 (Linux/Mac)
├── start_chrome.bat          # Chrome 실행 스크립트 (Windows)
│
├── src/                      # 소스 코드
│   ├── __init__.py
│   ├── citation_agent.py     # AI Agent 로직
│   ├── paper_search.py       # 논문 검색 엔진
│   ├── overleaf_controller.py # Overleaf 제어
│   └── config.py             # 설정 관리
│
└── examples/                 # 예시 파일
    ├── sample.tex           # 샘플 LaTeX 문서
    └── references.bib       # 샘플 BibTeX 파일
```

## 주요 컴포넌트

### 1. Citation Agent (`src/citation_agent.py`)
- Upstage Solar Pro 2 LLM 사용
- Function Calling으로 논문 검색 및 BibTeX 생성
- 인용 필요성 자동 판단
- 캐시로 중복 검색 방지

### 2. Paper Searcher (`src/paper_search.py`)
- Semantic Scholar API 연동
- 논문 메타데이터 추출
- BibTeX 엔트리 자동 생성
- Citation key 자동 생성 (예: `vaswani2017attention`)

### 3. Overleaf Controller (`src/overleaf_controller.py`)
- Selenium WebDriver로 브라우저 제어
- Chrome Remote Debugging Protocol 사용
- ACE Editor JavaScript Injection
- 텍스트 읽기/쓰기/교체 기능

### 4. Main CLI (`main.py`)
- 3가지 실행 모드:
  - **Interactive**: 선택된 텍스트만 처리
  - **Full Document**: 문서 전체 처리
  - **File**: 로컬 파일 처리 (Overleaf 불필요)

## 설치 및 실행

### 빠른 시작 (5분)

```bash
# 1. 의존성 설치
cd /mnt/ddn/kyudan/citeAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 설정
cp config.yaml.example config.yaml
# config.yaml에서 API 키 입력

# 3. 환경 검증
python verify_setup.py

# 4. Chrome 실행 (별도 터미널)
./start_chrome.sh

# 5. Overleaf 접속 (Chrome에서)
# https://www.overleaf.com → 로그인 → 프로젝트 열기

# 6. CiteAgent 실행
python main.py --interactive
```

### 테스트 (Overleaf 없이)

```bash
# 논문 검색 테스트
python test_agent.py --test search

# 전체 기능 테스트
python test_agent.py --test all

# 예시 파일 처리
python main.py --file examples/sample.tex
```

## 사용 예시

### Before:
```latex
Transformers have revolutionized natural language processing.
```

### After:
```latex
Transformers have revolutionized natural language processing \citep{vaswani2017attention}.
```

### Auto-generated BibTeX:
```bibtex
@inproceedings{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  booktitle={Advances in neural information processing systems},
  year={2017}
}
```

## 구성 요소별 상태

| 컴포넌트 | 상태 | 설명 |
|---------|------|------|
| Paper Search | ✅ 완성 | Semantic Scholar API 연동 |
| BibTeX Generation | ✅ 완성 | 자동 키 생성 및 포맷팅 |
| Citation Agent | ✅ 완성 | Function Calling 구현 |
| Overleaf Controller | ✅ 완성 | ACE Editor 제어 |
| Interactive Mode | ✅ 완성 | 선택 텍스트 처리 |
| Full Document Mode | ✅ 완성 | 전체 문서 처리 |
| File Mode | ✅ 완성 | 오프라인 처리 |
| Configuration | ✅ 완성 | YAML + 환경변수 |
| Error Handling | ✅ 완성 | 사용자 친화적 에러 메시지 |
| Documentation | ✅ 완성 | README, 가이드, 예시 |
| Test Scripts | ✅ 완성 | verify_setup, test_agent |

## 필요한 외부 서비스

### 1. Upstage API
- **용도**: LLM (인용 판단 및 텍스트 생성)
- **가입**: https://console.upstage.ai/
- **비용**: Free tier 사용 가능
- **설정**: config.yaml에 API 키 입력

### 2. Semantic Scholar API
- **용도**: 논문 검색
- **가입**: 불필요 (무료 공개 API)
- **제한**: Rate limit 존재 (충분히 관대함)
- **설정**: 없음

### 3. Chrome Browser
- **용도**: Overleaf 제어
- **다운로드**: https://www.google.com/chrome/
- **요구사항**: Remote debugging 지원 버전

## 제약사항 및 주의사항

### 기술적 제약
1. **Overleaf UI 의존성**: Overleaf UI 변경 시 일부 기능 동작 안 할 수 있음
2. **ACE Editor 의존성**: 다른 에디터 사용하는 플랫폼은 지원 안 됨
3. **Chrome 전용**: Firefox 등 다른 브라우저 미지원

### 사용상 주의
1. **백업 필수**: Full Document 모드는 문서 전체 교체
2. **검토 필수**: 자동 생성된 인용은 반드시 확인
3. **API 한도**: 과도한 사용 시 Rate limit 가능

### 보안
1. **API 키 관리**: config.yaml을 Git에 커밋하지 말 것
2. **Chrome Profile**: 개인 정보 격리됨
3. **JavaScript Injection**: 사용자 입력 검증됨

## 향후 개선 가능사항

### 단기 (쉬움)
- [ ] 여러 .bib 파일 지원
- [ ] 다른 인용 스타일 (APA, Chicago 등)
- [ ] 캐시를 디스크에 저장
- [ ] 진행률 표시 (Progress bar)

### 중기 (중간)
- [ ] GUI 버전 (Tkinter 또는 웹 인터페이스)
- [ ] 병렬 처리 (여러 문단 동시 처리)
- [ ] arXiv API 추가 지원
- [ ] PubMed API 추가 지원

### 장기 (어려움)
- [ ] VS Code Extension
- [ ] 다른 에디터 지원 (TeXstudio 등)
- [ ] 로컬 LLM 지원 (Ollama, LM Studio)
- [ ] 커뮤니티 피드백 기반 논문 추천

## 문서

| 문서 | 용도 |
|------|------|
| [README.md](README.md) | 설치, 설정, 기본 사용법 |
| [QUICKSTART.md](QUICKSTART.md) | 5분 빠른 시작 |
| [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) | 상세 사용 예시 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 내부 구조 및 기술 세부사항 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 이 파일 (프로젝트 개요) |

## 라이선스

MIT License (자유롭게 사용, 수정, 배포 가능)

## 기여

이슈 및 Pull Request 환영합니다!

## 제작자 노트

이 프로젝트는 학술 논문 작성의 고충을 해결하기 위해 만들어졌습니다.
특히 다음과 같은 분들에게 유용할 것입니다:

- 논문을 쓰면서 관련 연구를 찾아 인용하는 것이 번거로운 연구자
- 인용 형식을 맞추는 것이 귀찮은 학생
- 초안 작성 후 일괄적으로 인용을 추가하고 싶은 저자

**주의**: 이 도구는 보조 도구일 뿐입니다. 생성된 인용은 반드시 검토하고,
학술적 정직성을 유지하는 것은 사용자의 책임입니다.

---

**Happy writing! 📝✨**

For questions or issues, please check the documentation or create an issue on GitHub.
