# CiteAgent Architecture

이 문서는 CiteAgent의 내부 구조와 작동 방식을 설명합니다.

## 시스템 개요

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                    main.py (CLI)                            │
│  - Interactive Mode                                         │
│  - Full Document Mode                                       │
│  - File Mode                                                │
└────────┬────────────────────────────────┬───────────────────┘
         │                                │
         ↓                                ↓
┌──────────────────┐          ┌─────────────────────────┐
│ Overleaf         │          │  Citation Agent         │
│ Controller       │          │  (src/citation_agent.py)│
│ (Selenium)       │          │                         │
└────────┬─────────┘          └──────────┬──────────────┘
         │                               │
         │ Read/Write                    │ Function Calling
         │ LaTeX                         │
         │                               ↓
         │                    ┌─────────────────────────┐
         │                    │ Upstage Solar Pro 2 API │
         │                    │ (LLM + Function Calling)│
         │                    └──────────┬──────────────┘
         │                               │
         │                    ┌──────────┴──────────────┐
         │                    │                         │
         │                    ↓                         ↓
         │         ┌──────────────────┐    ┌────────────────────┐
         │         │  Paper Searcher  │    │  BibTeX Generator  │
         │         │ (Semantic Scholar)│   │                    │
         │         └──────────────────┘    └────────────────────┘
         │                    │                         │
         │                    └──────────┬──────────────┘
         │                               │
         ↓                               ↓
┌─────────────────────────────────────────────────────────────┐
│                    Overleaf Document                        │
│  - main.tex (updated with citations)                       │
│  - references.bib (updated with BibTeX entries)            │
└─────────────────────────────────────────────────────────────┘
```

## 핵심 컴포넌트

### 1. main.py - Entry Point

**역할**: 사용자 인터페이스 및 워크플로우 관리

**주요 기능**:
- CLI 인터페이스 제공
- 세 가지 실행 모드 지원:
  - Interactive: 선택된 텍스트 처리
  - Full Document: 전체 문서 처리
  - File: 로컬 파일 처리
- 구성 요소 초기화 및 조율

### 2. src/citation_agent.py - AI Agent Core

**역할**: LLM 기반 인용 추가 로직

**클래스**: `CitationAgent`

**주요 메서드**:
- `process_text(latex_text)`: 텍스트 처리 및 인용 추가
- `_search_paper_tool(query)`: 논문 검색 도구 함수
- `_get_bibtex_tool(paper_key)`: BibTeX 생성 도구 함수

**작동 방식**:
1. LaTeX 텍스트를 LLM에 전달
2. LLM이 인용 필요성 판단
3. Function Calling으로 도구 호출
4. 검색 결과 기반 최종 텍스트 생성

**캐싱**:
- `paper_cache`: 검색 결과 캐시
- `bibtex_cache`: BibTeX 엔트리 캐시

### 3. src/paper_search.py - Paper Search Engine

**역할**: 논문 검색 및 메타데이터 관리

**클래스**:
- `Paper`: 논문 데이터 클래스
- `PaperSearcher`: 검색 엔진

**주요 메서드**:
- `search_papers(query, limit, min_citations)`: 논문 검색
- `get_paper_details(paper_id)`: 논문 상세 정보 조회
- `generate_bibtex_key(paper)`: BibTeX 키 생성
- `generate_bibtex_entry(paper)`: BibTeX 엔트리 생성

**API**: Semantic Scholar Graph API
- 엔드포인트: `https://api.semanticscholar.org/graph/v1`
- 인증 불필요 (기본 사용량 한도)
- 응답 필드: title, authors, year, citationCount, externalIds, abstract

### 4. src/overleaf_controller.py - Browser Automation

**역할**: Overleaf 브라우저 자동화

**클래스**: `OverleafController`

**주요 메서드**:
- `connect()`: Chrome 디버깅 포트로 연결
- `get_editor_content()`: ACE 에디터 내용 읽기
- `set_editor_content(content)`: 에디터 내용 쓰기
- `get_selected_text()`: 선택된 텍스트 가져오기
- `replace_selected_text(new_text)`: 선택 영역 교체
- `switch_to_file(filename)`: 파일 전환
- `append_to_bib_file(entries)`: BibTeX 파일에 추가

**기술 스택**:
- Selenium WebDriver
- Chrome DevTools Protocol (원격 디버깅)
- JavaScript Injection (ACE Editor 제어)

### 5. src/config.py - Configuration Management

**역할**: 설정 파일 및 환경변수 관리

**클래스**: `Config`

**설정 소스**:
1. `config.yaml` 파일
2. 환경변수 (우선순위 높음)

**주요 메서드**:
- `get(key_path, default)`: 설정 값 조회
- `get_upstage_api_key()`: API 키 조회
- `get_upstage_config()`: Upstage 설정
- `get_chrome_config()`: Chrome 설정
- `get_agent_config()`: Agent 설정

## 데이터 플로우

### Interactive Mode 워크플로우

```
1. User selects text in Overleaf
   ↓
2. OverleafController.get_selected_text()
   ↓
3. CitationAgent.process_text(selected_text)
   ↓
4. LLM analyzes text
   ↓
5. LLM calls search_paper("transformer attention")
   ↓
6. PaperSearcher.search_papers("transformer attention")
   ↓
7. Semantic Scholar API returns results
   ↓
8. LLM selects best paper
   ↓
9. LLM calls get_bibtex("vaswani2017attention")
   ↓
10. generate_bibtex_entry(paper) returns BibTeX
   ↓
11. LLM generates text with \citep{vaswani2017attention}
   ↓
12. User confirms
   ↓
13. OverleafController.replace_selected_text(modified)
   ↓
14. OverleafController.append_to_bib_file(bibtex)
   ↓
15. Done!
```

## Function Calling 상세

### Solar Pro 2 Function Calling

Upstage Solar Pro 2는 OpenAI와 호환되는 Function Calling API를 제공합니다.

**Tool Definition 예시**:
```python
{
    "type": "function",
    "function": {
        "name": "search_paper",
        "description": "Search for academic papers...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "..."},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
}
```

**호출 흐름**:
1. Client → LLM: 메시지 + 도구 정의
2. LLM → Client: 도구 호출 요청 (`tool_calls`)
3. Client: 도구 함수 실행
4. Client → LLM: 도구 실행 결과
5. LLM → Client: 최종 응답 생성

## Overleaf ACE Editor 제어

### JavaScript Injection

Overleaf는 ACE Editor를 사용하므로, Selenium의 `execute_script()`로 JavaScript를 주입하여 제어합니다.

**읽기**:
```javascript
window.aceEditor ? window.aceEditor.getValue() :
ace.edit('editor') ? ace.edit('editor').getValue() : null;
```

**쓰기**:
```javascript
var editor = window.aceEditor || ace.edit('editor');
if (editor) {
    editor.setValue(content, -1);  // -1: cursor to start
}
```

**선택 영역 교체**:
```javascript
var editor = window.aceEditor || ace.edit('editor');
if (editor) {
    editor.session.replace(
        editor.selection.getRange(),
        newText
    );
}
```

### Chrome Remote Debugging

**연결 방법**:
```python
chrome_options = Options()
chrome_options.add_experimental_option(
    "debuggerAddress", "127.0.0.1:9222"
)
driver = webdriver.Chrome(options=chrome_options)
```

**장점**:
- 기존 세션 유지 (로그인 상태 보존)
- 캡차 우회
- 사용자가 브라우저를 직접 제어 가능

## 에러 처리 및 복원력

### 네트워크 에러

**Semantic Scholar API**:
- Timeout: 10초
- Retry: 현재 미구현 (향후 추가 가능)
- Fallback: 빈 리스트 반환

**Upstage API**:
- OpenAI Python SDK의 자동 재시도 사용
- 에러 발생 시 예외 전파

### Overleaf 연결 실패

1. 포트 확인
2. URL 확인 (`overleaf.com` 포함 여부)
3. 에러 메시지로 사용자 안내

### 캐싱 전략

**목적**: API 호출 최소화, 비용 절감

**구현**:
- In-memory 딕셔너리
- 세션 단위 (프로그램 종료 시 초기화)

**향후 개선**:
- 디스크 캐시 (SQLite, Redis)
- TTL (Time-To-Live)
- 캐시 무효화 전략

## 확장 가능성

### 다른 검색 엔진 추가

`PaperSearcher` 인터페이스를 구현하여 다른 API 추가 가능:
- arXiv API
- PubMed
- Google Scholar (비공식 API)

### 다른 LLM 사용

OpenAI 호환 API면 교체 가능:
- OpenAI GPT-4
- Anthropic Claude (via proxy)
- Local LLM (LM Studio, Ollama)

### 다른 에디터 지원

- VS Code + LaTeX Workshop
- TeXstudio
- Overleaf Desktop (Electron)

## 보안 고려사항

### API 키 관리

- 파일: `config.yaml` (gitignore 필수)
- 환경변수: `UPSTAGE_API_KEY`
- 절대 코드에 하드코딩 금지

### JavaScript Injection

- 사용자 입력 검증
- `json.dumps()`로 이스케이프
- XSS 방지

### Overleaf 세션

- Chrome Profile 격리
- 세션 토큰 비저장
- 읽기 전용 모드 옵션 (향후)

## 성능 최적화

### 병렬 처리

현재 순차 처리 → 향후 개선:
- 여러 문단 동시 처리
- Batch API 호출

### 토큰 사용량 최적화

- 긴 문서는 섹션 단위 분할
- 요약된 검색 결과 전달
- Temperature 낮게 설정 (0.3)

## 테스트 전략

### 단위 테스트

- `test_agent.py`: 기본 기능 검증
- `verify_setup.py`: 환경 검증

### 통합 테스트

- 예제 파일: `examples/sample.tex`
- End-to-end 워크플로우

### 수동 테스트

- Interactive 모드로 실제 논문 작성
- Edge case 확인

## 참고 자료

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [ACE Editor API](https://ace.c9.io/#nav=api)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [Upstage Docs](https://developers.upstage.ai/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
