# CiteAgent 시작하기 - 체크리스트

이 문서를 따라하면 CiteAgent를 성공적으로 설정하고 사용할 수 있습니다.

## 📋 설치 체크리스트

### 1단계: 시스템 요구사항 확인

- [ ] Python 3.8 이상 설치됨
  ```bash
  python3 --version
  # Python 3.8.x 이상이어야 함
  ```

- [ ] Google Chrome 설치됨
  ```bash
  # Mac
  ls "/Applications/Google Chrome.app"

  # Linux
  which google-chrome
  ```

- [ ] Git 설치됨 (선택사항, 이미 클론했다면 불필요)
  ```bash
  git --version
  ```

### 2단계: 프로젝트 설정

- [ ] 프로젝트 디렉토리 이동
  ```bash
  cd /mnt/ddn/kyudan/citeAgent
  ```

- [ ] 가상환경 생성
  ```bash
  python3 -m venv venv
  ```

- [ ] 가상환경 활성화
  ```bash
  # Linux/Mac
  source venv/bin/activate

  # Windows
  venv\Scripts\activate
  ```

- [ ] 의존성 설치
  ```bash
  pip install -r requirements.txt
  ```

### 3단계: API 키 설정

- [ ] Upstage Console 방문
  - URL: https://console.upstage.ai/
  - 회원가입 또는 로그인

- [ ] API 키 생성
  - 메뉴: API Keys
  - "Create New Key" 클릭
  - 키 이름 입력 (예: "CiteAgent")
  - 키 복사

- [ ] 설정 파일 생성
  ```bash
  cp config.yaml.example config.yaml
  ```

- [ ] API 키 입력
  ```bash
  # 에디터로 열기
  nano config.yaml  # 또는 vim, code 등

  # 다음 줄 수정:
  # api_key: "your_upstage_api_key_here"
  # → 복사한 키로 교체
  ```

### 4단계: 환경 검증

- [ ] 검증 스크립트 실행
  ```bash
  python verify_setup.py
  ```

- [ ] 모든 체크 통과 확인
  ```
  ✓ Python Version (>=3.8)
  ✓ Python Dependencies
  ✓ Configuration File
  ✓ Google Chrome
  ✓ ChromeDriver
  ✓ Semantic Scholar API
  ✓ Upstage API

  Passed: 7/7 checks
  ```

**문제가 있다면?**
- ✗ 표시된 항목의 에러 메시지 확인
- [README.md](README.md)의 문제 해결 섹션 참고

---

## 🚀 첫 실행 체크리스트

### 옵션 A: 테스트 실행 (Overleaf 불필요)

가장 쉬운 방법! 먼저 Overleaf 없이 테스트해보세요.

- [ ] 논문 검색 테스트
  ```bash
  python test_agent.py --test search
  ```

  예상 출력:
  ```
  [PaperSearch] Searching for: 'transformer attention mechanism'
  [PaperSearch] Found 3 papers

  1. Attention is all you need
     Authors: Vaswani, Ashish, Shazeer, Noam, Parmar, Niki
     Year: 2017
     Citations: 50000+
  ```

- [ ] 전체 Agent 테스트
  ```bash
  python test_agent.py --test citation
  ```

- [ ] 예시 파일 처리
  ```bash
  python main.py --file examples/sample.tex
  ```

  생성 확인:
  ```bash
  ls examples/sample_cited.*
  # sample_cited.tex
  # sample_cited.bib
  ```

**성공했다면**: 핵심 기능이 모두 작동합니다! 이제 Overleaf와 연결할 준비가 되었습니다.

### 옵션 B: Overleaf와 연결

실제 논문에 사용하려면 이 단계를 진행하세요.

#### B-1. Chrome 디버깅 모드 실행

- [ ] 기존 Chrome 창 모두 닫기
  ```bash
  # Mac/Linux (선택사항)
  pkill -a -i "Google Chrome"
  ```

- [ ] 디버깅 모드로 Chrome 실행

  **자동 (권장)**:
  ```bash
  # Mac/Linux
  ./start_chrome.sh

  # Windows
  start_chrome.bat
  ```

  **수동**:
  ```bash
  # Mac
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/ChromeProfile"

  # Linux
  google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/ChromeProfile"
  ```

- [ ] Chrome이 열렸는지 확인

#### B-2. Overleaf 접속

- [ ] Chrome에서 Overleaf 열기
  - URL: https://www.overleaf.com

- [ ] 로그인

- [ ] 프로젝트 선택 (또는 새로 생성)

- [ ] `.tex` 파일 열기 (예: `main.tex`)

#### B-3. CiteAgent 실행

- [ ] 새 터미널 열기

- [ ] 가상환경 활성화 확인
  ```bash
  cd /mnt/ddn/kyudan/citeAgent
  source venv/bin/activate
  ```

- [ ] Interactive 모드 실행
  ```bash
  python main.py --interactive
  ```

- [ ] 연결 확인
  ```
  [Overleaf] Connecting to Chrome on port 9222...
  [Overleaf] Successfully connected!
  [Overleaf] Current URL: https://www.overleaf.com/project/xxxxx
  ```

#### B-4. 첫 인용 추가

- [ ] Overleaf에서 텍스트 선택
  - 간단한 문장 선택 (예: "Deep learning is powerful.")
  - 마우스로 드래그

- [ ] 터미널에서 Enter 키

- [ ] 처리 과정 관찰
  ```
  [CiteAgent] Processing 25 characters...
  [Agent] Analyzing text...
  [Agent] Calling tool: search_paper
  [PaperSearch] Searching for: ...
  ```

- [ ] 결과 확인
  ```
  --- Modified Text ---
  Deep learning is powerful \citep{lecun2015deep}.

  --- BibTeX Entries (1) ---
  @article{lecun2015deep,
    ...
  }

  [CiteAgent] Apply changes? (yes/no):
  ```

- [ ] `yes` 입력하여 적용

- [ ] Overleaf에서 변경사항 확인
  - 선택한 텍스트가 인용과 함께 교체됨
  - `references.bib`에 BibTeX 추가됨 (파일 트리에서 확인)

**성공!** 🎉 이제 CiteAgent를 사용할 수 있습니다!

---

## 📚 다음 단계

### 배우기

- [ ] [QUICKSTART.md](QUICKSTART.md) 읽기 - 5분 가이드
- [ ] [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) 읽기 - 상세 예시
- [ ] [README.md](README.md) 읽기 - 전체 기능

### 실전 사용

- [ ] 작성 중인 논문의 Introduction 섹션으로 시도
- [ ] Related Work 섹션으로 시도
- [ ] 전체 문서 백업 후 Full Document 모드 시도

### 고급 기능

- [ ] [ARCHITECTURE.md](ARCHITECTURE.md) 읽기 - 내부 구조 이해
- [ ] 설정 커스터마이징 (`config.yaml`)
- [ ] 다른 인용 스타일 실험

---

## ❓ 문제 해결 빠른 참조

### "Could not connect to Overleaf"
→ Chrome 재시작 (`./start_chrome.sh`)

### "API key not found"
→ `config.yaml` 확인, API 키 제대로 입력했는지

### "No papers found"
→ 인터넷 연결 확인, 더 구체적인 텍스트로 시도

### "Could not find ACE editor"
→ Overleaf 페이지 새로고침, `.tex` 파일 열려있는지 확인

### 기타 문제
→ [README.md - 문제 해결](README.md#문제-해결) 참고

---

## 💡 유용한 팁

### 1. 백업 습관
중요한 작업 전 항상 백업하세요:
- Overleaf의 "History" 기능 활용
- 또는 File 모드로 로컬에 먼저 테스트

### 2. 점진적 사용
처음엔 작은 부분부터:
1. 문장 하나로 시작
2. 문단으로 확장
3. 섹션 전체
4. 문서 전체

### 3. 검토는 필수
자동 생성된 인용을 항상 확인하세요:
- 논문이 실제로 관련있는지
- 인용 위치가 적절한지
- BibTeX 정보가 정확한지

### 4. 효율적인 워크플로우
```
1. 초안 작성 (인용 없이)
2. Interactive 모드로 섹션별 처리
3. 수동으로 검토 및 조정
4. LaTeX 컴파일하여 확인
```

---

## 🎓 학습 자료

| 문서 | 시간 | 난이도 |
|------|------|--------|
| [QUICKSTART.md](QUICKSTART.md) | 5분 | 초급 |
| [README.md](README.md) | 15분 | 초급 |
| [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) | 20분 | 중급 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 30분 | 고급 |

---

## ✅ 완료 확인

모든 체크박스를 완료했다면 축하합니다! 🎉

이제 당신은:
- ✅ CiteAgent를 설치했습니다
- ✅ 환경이 올바르게 설정되었습니다
- ✅ 첫 인용을 성공적으로 추가했습니다
- ✅ 기본 사용법을 이해했습니다

**Happy writing! 📝**

궁금한 점이 있다면:
- 문서를 다시 읽어보세요
- 에러 메시지를 자세히 확인하세요
- 간단한 예시부터 시작하세요

---

*Last updated: 2026-01-02*
