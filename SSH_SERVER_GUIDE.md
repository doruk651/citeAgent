# SSH 서버에서 CiteAgent 사용하기

SSH 서버에는 GUI가 없어서 Safari/Chrome을 직접 실행할 수 없습니다.
여러 해결 방법을 제시합니다.

## 문제 상황

```
[Overleaf] Safari connection failed: Unable to obtain driver for safari
```

**원인**: SSH 서버에는 디스플레이가 없어서 브라우저를 실행할 수 없음

## 🎯 해결책 비교

| 방법 | 난이도 | 속도 | 추천도 |
|------|--------|------|--------|
| 1. 로컬 맥북 실행 | ⭐ 쉬움 | ⚡ 빠름 | ⭐⭐⭐⭐⭐ |
| 2. File 모드 | ⭐⭐ 보통 | ⚡⚡ 보통 | ⭐⭐⭐⭐ |
| 3. VS Code Remote | ⭐⭐ 보통 | ⚡ 빠름 | ⭐⭐⭐⭐⭐ |
| 4. X11 Forwarding | ⭐⭐⭐⭐ 어려움 | 🐌 느림 | ⭐ |

---

## 해결책 1: 로컬 맥북에서 실행 ⭐⭐⭐⭐⭐

가장 간단하고 빠른 방법입니다.

### 1단계: 프로젝트 복사

```bash
# 로컬 맥북 터미널에서
scp -r nsml@node0:/mnt/ddn/kyudan/citeAgent ~/Desktop/citeAgent
```

### 2단계: 로컬에서 설정

```bash
cd ~/Desktop/citeAgent

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# Safari 설정 확인 (이미 했음)
# Safari → Preferences → Advanced → Show Develop menu ✅
# Develop → Allow Remote Automation ✅
```

### 3단계: 실행

```bash
python main.py -i -u "https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"
```

**장점**:
- ✅ Safari가 로컬에서 정상 실행
- ✅ 빠르고 안정적
- ✅ GUI 완벽 지원

**단점**:
- ❌ 서버의 큰 파일/데이터 접근 불가
- ❌ 프로젝트 복사 필요

---

## 해결책 2: File 모드 (브라우저 불필요) ⭐⭐⭐⭐

브라우저 없이 `.tex` 파일만 처리하는 방법입니다.

### 워크플로우

```
Overleaf → Download → Server Processing → Upload to Overleaf
```

### 단계별 실행

#### 1. Overleaf에서 파일 다운로드

1. Overleaf 프로젝트 열기
2. **Menu** → **Download** → **Source**
3. 압축 파일 다운로드 (예: `project.zip`)

#### 2. 서버에 업로드

```bash
# 로컬 맥북에서
cd ~/Downloads
unzip project.zip -d project
cd project

# main.tex를 서버로 전송
scp main.tex nsml@node0:/mnt/ddn/kyudan/citeAgent/
```

#### 3. 서버에서 처리

```bash
# SSH로 서버 접속
ssh nsml@node0

# CiteAgent 실행
cd /mnt/ddn/kyudan/citeAgent
source venv/bin/activate
python main.py --file main.tex

# 결과 확인
ls main_cited.tex main_cited.bib
```

출력:
```
main_cited.tex   # 인용이 추가된 파일
main_cited.bib   # BibTeX 엔트리
```

#### 4. 로컬로 다운로드

```bash
# 로컬 맥북에서
scp nsml@node0:/mnt/ddn/kyudan/citeAgent/main_cited.* ~/Downloads/
```

#### 5. Overleaf에 업로드

**Option A**: 파일 교체
1. Overleaf에서 `main.tex` 내용 전체 삭제
2. `main_cited.tex` 내용 복사 → 붙여넣기
3. `references.bib` 열기
4. `main_cited.bib` 내용 복사 → 붙여넣기

**Option B**: Upload
1. Overleaf Menu → Upload
2. `main_cited.tex`, `main_cited.bib` 업로드

**장점**:
- ✅ 브라우저 불필요
- ✅ 서버에서 실행 가능
- ✅ 안정적

**단점**:
- ❌ 수동으로 파일 업로드/다운로드 필요
- ❌ Interactive 모드 불가

---

## 해결책 3: VS Code Remote SSH ⭐⭐⭐⭐⭐

VS Code로 서버에 접속하면서 로컬 브라우저를 사용하는 방법입니다.

### 설정 방법

#### 1. VS Code Remote SSH 설치

1. VS Code 설치 (로컬 맥북)
2. Extension 설치: **Remote - SSH**
3. `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
4. `nsml@node0` 입력

#### 2. 서버에서 코드 열기

VS Code가 서버에 연결되면:
1. **File → Open Folder**
2. `/mnt/ddn/kyudan/citeAgent` 선택

#### 3. 터미널에서 실행

VS Code 내장 터미널에서:
```bash
# 이미 서버에 있음
source venv/bin/activate

# File 모드로 실행
python main.py --file examples/sample.tex
```

#### 4. Port Forwarding으로 브라우저 연동 (고급)

VS Code의 Port Forwarding 기능을 사용하면 서버의 특정 포트를 로컬로 연결 가능.

하지만 CiteAgent는 직접 브라우저 제어가 필요하므로, **File 모드**가 더 적합합니다.

**장점**:
- ✅ 서버 환경 그대로 사용
- ✅ 코드 편집 용이
- ✅ 통합 개발 환경

**단점**:
- ❌ 브라우저 자동화는 여전히 제한적
- ❌ File 모드만 실용적

---

## 해결책 4: X11 Forwarding (비추천) ⭐

GUI를 SSH로 forwarding하는 방법입니다.

### 설정 (복잡함)

```bash
# 로컬 맥북에 XQuartz 설치
brew install --cask xquartz

# XQuartz 실행 후 재부팅

# SSH 연결 (X11 forwarding)
ssh -X nsml@node0

# 서버에서
export DISPLAY=localhost:10.0
python main.py -i -u "URL"
```

**문제점**:
- 🐌 매우 느림 (네트워크 지연)
- 💥 자주 끊김
- 🔧 설정 복잡

**비추천합니다!**

---

## 권장 워크플로우

### 시나리오 1: 빠른 테스트
→ **로컬 맥북에서 실행** (해결책 1)

```bash
# 로컬
cd ~/Desktop
git clone <your-repo> citeAgent
cd citeAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py -i -u "URL"
```

### 시나리오 2: 서버 리소스 필요
→ **File 모드** (해결책 2)

```bash
# 서버에서
python main.py --file document.tex

# 로컬로 다운로드
scp nsml@node0:/path/to/document_cited.* .
```

### 시나리오 3: 개발 작업
→ **VS Code Remote SSH** (해결책 3)

---

## 자동화 스크립트

서버에서 자주 사용한다면 스크립트를 만드세요:

```bash
#!/bin/bash
# process_tex.sh - 서버에서 .tex 파일 처리

if [ -z "$1" ]; then
    echo "Usage: ./process_tex.sh <file.tex>"
    exit 1
fi

INPUT_FILE="$1"
cd /mnt/ddn/kyudan/citeAgent
source venv/bin/activate

echo "Processing $INPUT_FILE..."
python main.py --file "$INPUT_FILE"

OUTPUT_FILE="${INPUT_FILE%.tex}_cited.tex"
BIB_FILE="${INPUT_FILE%.tex}_cited.bib"

echo ""
echo "✅ Done!"
echo "Output: $OUTPUT_FILE"
echo "BibTeX: $BIB_FILE"
echo ""
echo "Download with:"
echo "  scp nsml@node0:/mnt/ddn/kyudan/citeAgent/$OUTPUT_FILE ."
echo "  scp nsml@node0:/mnt/ddn/kyudan/citeAgent/$BIB_FILE ."
```

사용:
```bash
chmod +x process_tex.sh
./process_tex.sh main.tex
```

---

## 요약

| 상황 | 추천 방법 |
|------|-----------|
| 빠르게 테스트하고 싶다 | 로컬 맥북 실행 |
| 서버 파일만 처리하면 됨 | File 모드 |
| 개발하면서 테스트 | VS Code Remote |
| GUI 꼭 필요 | 로컬 맥북 실행 |

**가장 추천**:
1. 🥇 로컬 맥북에서 실행 (가장 빠르고 쉬움)
2. 🥈 File 모드 (서버에서 처리 필요시)

SSH 서버에서 브라우저 자동화는 기술적으로 매우 어렵고 비효율적입니다.
**로컬 맥북에서 실행**하는 것이 최선입니다! 🎯
