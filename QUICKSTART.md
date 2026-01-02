# CiteAgent 빠른 시작 가이드

5분 안에 CiteAgent를 실행하는 방법입니다.

## 1단계: 설치 (2분)

```bash
cd /mnt/ddn/kyudan/citeAgent

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 2단계: 설정 (1분)

```bash
# 설정 파일 복사
cp config.yaml.example config.yaml

# API 키 설정 (에디터로 열어서 수정)
nano config.yaml  # 또는 vim, code 등
```

`config.yaml`에서 다음 부분 수정:
```yaml
upstage:
  api_key: "여기에_실제_API_키_입력"  # ← 이 부분만 수정
```

**API 키 받는 방법:**
- https://console.upstage.ai/ 접속
- 로그인 → API Keys → 새 키 생성

## 3단계: 테스트 (1분)

```bash
# 간단한 테스트
python test_agent.py --test search
```

논문 검색이 잘 되면 성공!

## 4단계: Overleaf와 연결 (1분)

### Chrome 디버깅 모드 실행

**Linux/Mac:**
```bash
./start_chrome.sh
```

**Windows:**
```
start_chrome.bat
```

또는 수동으로:

**Mac:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/ChromeProfile"
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/ChromeProfile"
```

### Overleaf 열기

1. 열린 Chrome에서 https://www.overleaf.com 접속
2. 로그인
3. 프로젝트 열기
4. `.tex` 파일 선택

## 5단계: 실행! (30초)

```bash
python main.py --interactive
```

**사용법:**
1. Overleaf에서 텍스트 선택 (드래그)
2. 터미널에서 Enter
3. 결과 확인 후 `yes` 입력
4. 완료!

## 예시

**처리 전:**
```latex
Transformers have revolutionized natural language processing.
```

**처리 후:**
```latex
Transformers have revolutionized natural language processing \citep{vaswani2017attention}.
```

**자동 생성된 BibTeX:**
```bibtex
@inproceedings{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and others},
  year={2017}
}
```

## 문제가 생겼나요?

### "Could not connect to Overleaf"
→ Chrome을 모두 닫고 디버깅 모드로 다시 시작

### "API key not found"
→ config.yaml에 API 키가 제대로 입력되었는지 확인

### "No papers found"
→ 인터넷 연결 확인, 또는 다른 텍스트로 시도

## 다음 단계

- [README.md](README.md) - 전체 문서
- [고급 기능 사용법](README.md#고급-사용법)
- 문제 해결: [README.md](README.md#문제-해결)

---

**즐거운 논문 작성 되세요! 🎓**
