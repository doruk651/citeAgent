# Safari에서 CiteAgent 빠른 시작 (3분)

Safari 사용자를 위한 초간단 가이드입니다.

## 1단계: Safari 설정 (1분, 최초 1회만)

### Safari Preferences 열기
`Cmd + ,` 또는 Safari → Preferences

### Advanced 탭에서
✅ "Show Develop menu in menu bar" 체크

### Develop 메뉴에서
✅ "Allow Remote Automation" 체크

### 터미널에서 실행
```bash
sudo safaridriver --enable
```
비밀번호 입력하고 완료!

## 2단계: CiteAgent 설정 (30초)

### config.yaml 수정
```bash
cd /mnt/ddn/kyudan/citeAgent
nano config.yaml  # 또는 다른 에디터
```

이 부분만 수정:
```yaml
browser:
  type: "safari"  # 이 줄만 chrome → safari로 변경
```

저장하고 닫기 (`Ctrl+X`, `Y`, `Enter`)

## 3단계: 실행! (1분)

```bash
# CiteAgent 실행
python main.py --interactive
```

**자동으로 Safari가 열립니다!**

1. Safari에서 Overleaf 로그인
2. 프로젝트 열기
3. 터미널에서 **Enter**
4. Overleaf에서 텍스트 선택
5. 터미널에서 **Enter**
6. 완료!

## 처음 실행 시 예상 흐름

```bash
$ python main.py --interactive

======================================================================
  CiteAgent - Automated Citation Assistant for Overleaf
======================================================================

Mode: Interactive

[Overleaf] Connecting to Safari...
[Overleaf] Safari opened. Please navigate to your Overleaf project.
[Overleaf] Press Enter when you're on the Overleaf editor page...
```

**여기서**: Safari에서 Overleaf 로그인 → 프로젝트 열기 → Enter

```
[Overleaf] Successfully connected!
[Overleaf] Current URL: https://www.overleaf.com/project/xxxxx

[CiteAgent] Press Enter to process selection (or 'quit'):
```

**여기서**: Overleaf에서 텍스트 선택 → Enter

```
[CiteAgent] Processing 150 characters...

--- Selected Text ---
Transformers have revolutionized NLP.

[PaperSearch] Searching for: 'transformer natural language processing'
[PaperSearch] Found 5 papers
...

[CiteAgent] Apply changes? (yes/no):
```

**`yes` 입력** → 완료!

## 문제 해결

### "Safari could not connect"
→ Safari 설정 다시 확인 (위 1단계)
→ `sudo safaridriver --enable` 실행했는지 확인

### Safari가 안 열림
→ Safari를 수동으로 한 번 열었다가 닫기
→ 다시 CiteAgent 실행

### 권한 에러
→ `sudo safaridriver --enable` 다시 실행

## Chrome으로 바꾸고 싶다면?

`config.yaml`에서:
```yaml
browser:
  type: "chrome"  # safari → chrome으로 변경
```

그리고:
```bash
./start_chrome.sh  # Chrome 디버깅 모드 실행
```

---

**끝!** 이제 Safari에서 CiteAgent를 사용할 수 있습니다! 🎉

더 자세한 정보는 [SAFARI_SETUP.md](SAFARI_SETUP.md)를 참고하세요.
