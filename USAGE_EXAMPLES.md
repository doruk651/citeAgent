# CiteAgent 사용 예시

실제 사용 시나리오별 자세한 예시입니다.

## 목차

1. [기본 사용법](#1-기본-사용법)
2. [Interactive Mode 상세](#2-interactive-mode-상세)
3. [Full Document Mode](#3-full-document-mode)
4. [File Mode (오프라인)](#4-file-mode-오프라인)
5. [고급 시나리오](#5-고급-시나리오)
6. [문제 해결 예시](#6-문제-해결-예시)

---

## 1. 기본 사용법

### 시나리오: Introduction 섹션에 인용 추가

**원본 텍스트**:
```latex
\section{Introduction}

Deep learning has revolutionized computer vision. Convolutional neural
networks have achieved human-level performance on image classification tasks.
Recent work has shown that vision transformers can outperform CNNs.
```

**처리 과정**:

1. Overleaf에서 위 텍스트 전체 선택
2. 터미널에서 Enter
3. Agent가 분석하고 검색:

```
[Agent] Analyzing text and planning citations...
[Agent] Calling tool: search_paper
[Agent] Arguments: {'query': 'convolutional neural networks image classification', 'limit': 5}
[PaperSearch] Searching for: 'convolutional neural networks image classification'...
[PaperSearch] Found 5 papers

[Agent] Calling tool: search_paper
[Agent] Arguments: {'query': 'vision transformer', 'limit': 5}
[PaperSearch] Searching for: 'vision transformer'...
[PaperSearch] Found 5 papers

[Agent] Calling tool: get_bibtex
[Agent] Arguments: {'paper_key': 'krizhevsky2012imagenet'}
[Agent] Calling tool: get_bibtex
[Agent] Arguments: {'paper_key': 'dosovitskiy2020image'}
```

**결과 텍스트**:
```latex
\section{Introduction}

Deep learning has revolutionized computer vision. Convolutional neural
networks have achieved human-level performance on image classification
tasks \citep{krizhevsky2012imagenet}. Recent work has shown that vision
transformers can outperform CNNs \citep{dosovitskiy2020image}.
```

**BibTeX 엔트리**:
```bibtex
@inproceedings{krizhevsky2012imagenet,
  title={Imagenet classification with deep convolutional neural networks},
  author={Krizhevsky, Alex and Sutskever, Ilya and Hinton, Geoffrey E},
  booktitle={Advances in neural information processing systems},
  year={2012}
}

@article{dosovitskiy2020image,
  title={An image is worth 16x16 words: Transformers for image recognition at scale},
  author={Dosovitskiy, Alexey and Beyer, Lucas and Kolesnikov, Alexander and others},
  journal={arXiv preprint arXiv:2010.11929},
  year={2020}
}
```

---

## 2. Interactive Mode 상세

### 단계별 실행

#### 1단계: Chrome 실행
```bash
# Mac/Linux
./start_chrome.sh

# 또는 수동으로
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/ChromeProfile"
```

#### 2단계: Overleaf 접속
1. Chrome에서 https://www.overleaf.com 열기
2. 로그인
3. 프로젝트 선택
4. `main.tex` 또는 다른 `.tex` 파일 열기

#### 3단계: CiteAgent 실행
```bash
cd /mnt/ddn/kyudan/citeAgent
source venv/bin/activate  # 가상환경 활성화
python main.py --interactive
```

**출력 예시**:
```
======================================================================
  CiteAgent - Automated Citation Assistant for Overleaf
======================================================================

Mode: Interactive

Instructions:
1. Make sure Chrome is running with remote debugging enabled
2. Navigate to your Overleaf project
3. Select text in the editor that needs citations
4. Press Enter here to process the selection
5. Type 'quit' to exit

[Overleaf] Connecting to Chrome on port 9222...
[Overleaf] Successfully connected!
[Overleaf] Current URL: https://www.overleaf.com/project/xxxxx

[CiteAgent] Press Enter to process selection (or 'quit'):
```

#### 4단계: 텍스트 선택 및 처리
1. Overleaf 에디터에서 인용이 필요한 문단 드래그
2. 터미널에서 Enter

**처리 과정**:
```
[CiteAgent] Processing 234 characters...

--- Selected Text ---
Large language models have shown remarkable capabilities in natural
language understanding. However, they often suffer from hallucination
problems.

==============================================================
CITATION AGENT: Processing LaTeX Text
==============================================================

[Agent] Analyzing text and planning citations...

[Agent] Calling tool: search_paper
[Agent] Arguments: {'query': 'large language models hallucination', 'limit': 5}

[PaperSearch] Searching for: 'large language models hallucination'
[PaperSearch] Found 5 papers

[Agent] Calling tool: get_bibtex
[Agent] Arguments: {'paper_key': 'zhang2023siren'}

[Agent] Generating final text with citations...

==============================================================
CITATION AGENT: Processing Complete
==============================================================

--- Modified Text ---
Large language models have shown remarkable capabilities in natural
language understanding. However, they often suffer from hallucination
problems \citep{zhang2023siren}.

--- BibTeX Entries (1) ---
@article{zhang2023siren,
  title={Siren's Song in the AI Ocean: A Survey on Hallucination in Large Language Models},
  author={Zhang, Yue and Li, Yafu and others},
  journal={arXiv preprint arXiv:2309.01219},
  year={2023}
}

[CiteAgent] Apply changes? (yes/no): yes
[CiteAgent] ✓ Text updated in editor
[CiteAgent] ✓ BibTeX entries added to references.bib

[CiteAgent] Press Enter to process selection (or 'quit'):
```

#### 5단계: 반복 또는 종료
- 다른 텍스트 선택하고 Enter: 계속 처리
- `quit` 입력: 종료

---

## 3. Full Document Mode

### 전체 문서 한 번에 처리

#### 사용 시점
- 초안 완성 후 일괄 인용 추가
- 다른 사람이 쓴 문서에 인용 추가
- 백업 후 대량 처리

#### 안전한 방법: 파일로 저장

```bash
python main.py --full-document --output modified.tex
```

**결과**:
- `modified.tex`: 인용이 추가된 문서
- `modified.bib`: BibTeX 엔트리들

**검토 후 수동 적용**:
1. `modified.tex` 열어서 확인
2. 문제없으면 Overleaf에 복사-붙여넣기

#### 직접 적용 방법

```bash
python main.py --full-document
```

**주의사항**:
- 반드시 백업 먼저!
- 문서 전체가 교체됨
- Overleaf의 자동 저장으로 즉시 저장됨

**실행 예시**:
```
======================================================================
  CiteAgent - Automated Citation Assistant for Overleaf
======================================================================

Mode: Full Document

[Overleaf] Connecting to Chrome on port 9222...
[Overleaf] Successfully connected!
[Overleaf] Current URL: https://www.overleaf.com/project/xxxxx

[Overleaf] Reading editor content...
[Overleaf] Read 5432 characters

[CiteAgent] Processing document (5432 characters)...

[처리 과정 생략...]

[CiteAgent] Processing complete!
[CiteAgent] Found 12 papers to cite

[Warning] This will replace the ENTIRE document!
[CiteAgent] Apply changes to Overleaf? (yes/no): yes

[Overleaf] WARNING: This will replace ALL editor content!
[Overleaf] Make sure you have saved your work or have a backup.
[Overleaf] Continue? (yes/no): yes

[Overleaf] Writing to editor...
[Overleaf] Successfully wrote 5834 characters
[CiteAgent] ✓ Document updated
[CiteAgent] ✓ BibTeX entries added
```

---

## 4. File Mode (오프라인)

### 로컬 파일 처리

#### 장점
- Overleaf 연결 불필요
- 버전 관리 용이
- 스크립트에 통합 가능

#### 예시 1: 단일 파일

```bash
python main.py --file my_paper.tex
```

**입력 파일** (`my_paper.tex`):
```latex
\documentclass{article}
\begin{document}

Transformers have become the dominant architecture in NLP.
They rely on the self-attention mechanism.

\end{document}
```

**출력 파일**:
- `my_paper_cited.tex`: 인용 추가된 버전
- `my_paper_cited.bib`: BibTeX 엔트리

**my_paper_cited.tex**:
```latex
\documentclass{article}
\usepackage{natbib}
\begin{document}

Transformers have become the dominant architecture in NLP \citep{vaswani2017attention}.
They rely on the self-attention mechanism.

\bibliographystyle{plainnat}
\bibliography{my_paper_cited}
\end{document}
```

#### 예시 2: 섹션별 처리

논문이 여러 파일로 나뉘어 있는 경우:

```bash
# Introduction만 처리
python main.py --file sections/introduction.tex

# Related Work 처리
python main.py --file sections/related_work.tex

# Methods 처리
python main.py --file sections/methods.tex
```

각 섹션에 대한 `_cited.tex`와 `.bib` 파일이 생성됩니다.

#### 예시 3: 배치 처리 스크립트

```bash
#!/bin/bash
# process_all_sections.sh

for file in sections/*.tex; do
    echo "Processing $file..."
    python main.py --file "$file"
done

# 모든 BibTeX 합치기
cat sections/*_cited.bib > combined.bib

echo "Done! Combined BibTeX saved to combined.bib"
```

---

## 5. 고급 시나리오

### 시나리오 1: 특정 연도 이후 논문만

현재 config에서 설정:

```yaml
agent:
  min_citation_count: 50  # 인용 횟수 높이기
  temperature: 0.1        # 더 보수적으로
```

또는 코드에서 필터링 로직 추가 (고급 사용자)

### 시나리오 2: 다른 인용 스타일

LLM에게 지시:

텍스트 앞에 메타 지시문 추가:
```latex
% CITATION STYLE: Use \citet{} for in-text citations where author name appears

According to Vaswani et al., transformers work well.
```

→ LLM이 `\citet{vaswani2017attention}` 사용

### 시나리오 3: 특정 논문 우선

검색 결과에서 특정 키워드 우선:

```latex
The BERT model introduced masked language modeling.
% Prefer: Devlin et al. 2019, "BERT: Pre-training..."
```

### 시나리오 4: 여러 논문 동시 인용

```latex
Many studies have explored this topic.
```

→ Agent가 자동으로:
```latex
Many studies have explored this topic \citep{paper1,paper2,paper3}.
```

---

## 6. 문제 해결 예시

### 문제 1: 잘못된 논문 선택됨

**증상**:
```
Transformers use attention \citep{wrong2020paper}.
```

**해결**:
1. Interactive 모드에서 `no` 선택
2. 텍스트를 더 구체적으로 수정:
   ```
   Transformers, as introduced by Vaswani et al., use attention.
   ```
3. 다시 처리

### 문제 2: 인용이 추가되지 않음

**원인**: 텍스트가 너무 일반적

**예시**:
```latex
Deep learning is useful.
```

**해결**: 더 구체적인 주장 작성
```latex
Deep learning has achieved state-of-the-art results on ImageNet classification.
```

### 문제 3: BibTeX 파일에 추가 안됨

**수동 추가 방법**:

터미널에 출력된 BibTeX를 복사:
```bibtex
@article{zhang2023siren,
  title={...},
  ...
}
```

Overleaf에서:
1. `references.bib` 파일 클릭
2. 맨 아래에 붙여넣기

### 문제 4: API 호출 한도 초과

**증상**:
```
[Overleaf] Error: Rate limit exceeded
```

**해결**:
1. 잠시 대기 (1분)
2. 더 작은 단위로 나눠서 처리
3. 캐시 활용 (같은 쿼리 재사용)

### 문제 5: Chrome 연결 끊김

**증상**:
```
[Overleaf] Not connected!
```

**해결**:
```python
# CiteAgent 재실행
python main.py --interactive
```

자동으로 재연결 시도됨

---

## 실전 팁

### Tip 1: 초안 작성 후 한 번에 처리

1. 먼저 인용 없이 초안 완성
2. 백업 생성
3. Full Document 모드로 일괄 처리
4. 검토 후 수동 조정

### Tip 2: 중요한 인용은 수동으로

핵심 논문은 직접 추가하고, 부수적인 부분만 Agent 사용

### Tip 3: 섹션별 처리

Introduction, Related Work는 Interactive 모드로 신중하게
Methods, Results는 필요시 부분적으로만

### Tip 4: 검토는 필수

Agent가 생성한 인용을 항상 확인:
- 논문 제목과 내용 일치 여부
- 저자와 연도 정확성
- 인용 위치 적절성

### Tip 5: 캐시 활용

같은 세션에서 비슷한 텍스트 여러 번 처리하면 캐시 덕분에 빠름

---

## 실제 논문 작성 워크플로우

### 1단계: 초안 작성 (Overleaf, 인용 없이)
```latex
Transformers work well. They use attention.
Vision transformers are also good.
```

### 2단계: Interactive Mode로 섹션별 처리

**Introduction**:
- 선택 → Enter → 확인 → Apply

**Related Work**:
- 문단별로 선택 → Enter → 확인 → Apply

### 3단계: 검토 및 수정

생성된 인용 확인:
```latex
Transformers work well \citep{vaswani2017attention}.
They use attention \citep{bahdanau2014neural}.
Vision transformers are also good \citep{dosovitskiy2020image}.
```

### 4단계: BibTeX 정리

`references.bib` 확인:
- 중복 제거
- 형식 통일
- 누락된 필드 추가

### 5단계: 컴파일 및 최종 확인

Overleaf에서 PDF 생성 → 인용 제대로 나오는지 확인

---

**이제 CiteAgent로 논문 작성을 시작하세요! 🚀**

문제가 있으면 [README.md](README.md)의 문제 해결 섹션을 참고하거나,
[ARCHITECTURE.md](ARCHITECTURE.md)에서 내부 구조를 확인하세요.
