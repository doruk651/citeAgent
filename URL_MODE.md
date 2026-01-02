# Overleaf URL로 직접 접근하기

CiteAgent가 이제 **Overleaf 프로젝트 URL을 직접 받아서** 자동으로 접근할 수 있습니다!

## 사용 방법

### 1. Overleaf 공유 링크 받기

Overleaf 프로젝트에서:
1. 상단 **Share** 버튼 클릭
2. **Turn on link sharing** 활성화
3. **Anyone with this link can edit this project** 선택
4. 링크 복사 (예: `https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e`)

### 2. CiteAgent 실행

```bash
python main.py --interactive --url "https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"
```

또는 짧게:
```bash
python main.py -i -u "https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"
```

### 3. 자동 진행

CiteAgent가 자동으로:
1. ✅ Safari (또는 Chrome) 실행
2. ✅ Overleaf URL로 이동
3. ✅ 프로젝트 로드 대기
4. ✅ 에디터 준비 완료!

**텍스트를 선택하고 Enter를 누르면 인용이 추가됩니다!**

## 모든 모드에서 사용 가능

### Interactive 모드
```bash
python main.py --interactive --url "OVERLEAF_URL"
```

### Full Document 모드
```bash
python main.py --full-document --url "OVERLEAF_URL"
```

### 출력 파일로 저장
```bash
python main.py --full-document --url "OVERLEAF_URL" --output result.tex
```

## 실행 예시

```bash
$ python main.py -i -u "https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"

======================================================================
  CiteAgent - Automated Citation Assistant for Overleaf
======================================================================

Mode: Interactive

Overleaf URL: https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e

Instructions:
1. Browser will open and navigate to Overleaf
2. Select text in the editor that needs citations
3. Press Enter here to process the selection
4. Type 'quit' to exit

[Overleaf] Connecting to Safari...
[Overleaf] Enabling Safari Remote Automation...

[Overleaf] Navigating to: https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e
[Overleaf] Waiting for page to load...
[Overleaf] Waiting for editor to load...
[Overleaf] Successfully connected!
[Overleaf] Current URL: https://www.overleaf.com/project/8375755749spbdsnhhtktg

[CiteAgent] Press Enter to process selection (or 'quit'):
```

**여기서**: Overleaf에서 텍스트 선택 → Enter → 완료!

## Chrome 사용 시

Chrome을 사용하려면:

1. **Chrome 디버깅 모드 실행**:
```bash
./start_chrome.sh
```

2. **config.yaml 확인**:
```yaml
browser:
  type: "chrome"  # safari에서 chrome으로
```

3. **CiteAgent 실행**:
```bash
python main.py -i -u "OVERLEAF_URL"
```

## Safari 사용 시 (권장)

Safari는 설정이 더 간단합니다:

1. **Safari 설정** (최초 1회):
   - Safari → Preferences → Advanced → Show Develop menu ✅
   - Develop → Allow Remote Automation ✅
   - 터미널: `sudo safaridriver --enable`

2. **config.yaml 확인**:
```yaml
browser:
  type: "safari"
```

3. **CiteAgent 실행**:
```bash
python main.py -i -u "OVERLEAF_URL"
```

## 장점

### URL 모드 사용 시
- ✅ **자동 접근**: 수동으로 Overleaf 열 필요 없음
- ✅ **빠른 시작**: URL만 복사해서 실행
- ✅ **공유 가능**: 팀원과 같은 프로젝트 작업 가능
- ✅ **재현 가능**: 같은 명령어로 반복 실행

### URL 없이 사용 시
- ✅ **로그인 유지**: 이미 열린 브라우저 사용 (Chrome)
- ✅ **세션 유지**: 이전 작업 상태 그대로

## 주의사항

### 공유 링크 권한

Overleaf 공유 링크는 **편집 권한**이 있어야 합니다:
- ✅ "Anyone with this link can **edit** this project"
- ❌ "Anyone with this link can **view** this project" (읽기 전용은 안 됨)

### 로그인 필요 (Safari)

Safari를 사용하면 매번 로그인이 필요할 수 있습니다:
- **해결**: Overleaf에 로그인 상태 유지 설정
- **또는**: Chrome 사용 (세션 유지)

### 페이지 로딩 시간

프로젝트가 크면 로딩에 시간이 걸릴 수 있습니다:
- 현재: 기본 8초 대기 (3초 페이지 + 5초 에디터)
- 필요시 더 기다리면 됩니다

## 문제 해결

### "Failed to navigate to Overleaf"

**원인**: URL이 잘못되었거나 네트워크 문제

**해결**:
1. URL이 올바른지 확인
2. 브라우저에서 직접 열어보기
3. 인터넷 연결 확인

### "Permission denied"

**원인**: Overleaf 공유 링크가 읽기 전용

**해결**:
- Overleaf Share 설정에서 "Edit" 권한으로 변경

### 로그인 창이 뜸

**원인**: Overleaf에 로그인되어 있지 않음

**해결**:
1. 로그인하고 기다리기
2. 또는 Chrome 디버깅 모드 사용 (세션 유지)

## 고급 사용법

### 환경변수로 URL 설정

```bash
export OVERLEAF_URL="https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"
python main.py -i -u "$OVERLEAF_URL"
```

### 스크립트로 자동화

```bash
#!/bin/bash
# cite_my_paper.sh

OVERLEAF_URL="https://www.overleaf.com/8375755749spbdsnhhtktg#ecbc6e"

cd /mnt/ddn/kyudan/citeAgent
source venv/bin/activate

python main.py --interactive --url "$OVERLEAF_URL"
```

실행:
```bash
chmod +x cite_my_paper.sh
./cite_my_paper.sh
```

### 여러 프로젝트 관리

```bash
# 프로젝트 1
python main.py -i -u "https://www.overleaf.com/project1"

# 프로젝트 2
python main.py -i -u "https://www.overleaf.com/project2"
```

## 비교: URL vs 수동

| 방법 | URL 모드 | 수동 모드 |
|------|----------|-----------|
| **실행** | `python main.py -i -u URL` | `python main.py -i` |
| **브라우저** | 자동 실행 + 자동 이동 | 수동 실행 + 수동 이동 |
| **로그인** | 필요 (Safari) | Chrome은 유지 |
| **속도** | 약간 느림 (로딩 대기) | 빠름 (이미 열림) |
| **편의성** | ✅ 매우 높음 | 보통 |
| **자동화** | ✅ 가능 | 제한적 |

## 추천 사용 시나리오

### URL 모드를 사용하세요:
- 새 프로젝트 시작할 때
- 공유 받은 프로젝트 작업할 때
- 스크립트로 자동화하고 싶을 때
- Safari 사용 중일 때

### 수동 모드를 사용하세요:
- 이미 Overleaf가 열려 있을 때
- Chrome으로 로그인 유지하고 싶을 때
- 여러 프로젝트를 번갈아 작업할 때

---

**팁**: 둘 다 사용 가능합니다! 상황에 맞게 선택하세요. 😊
