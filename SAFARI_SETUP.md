# Safari 설정 가이드

CiteAgent는 Safari 브라우저도 지원합니다! 이 가이드를 따라 Safari에서 CiteAgent를 사용하세요.

## Safari 설정 (최초 1회만)

### 1단계: Develop 메뉴 활성화

1. Safari 열기
2. **Safari → Preferences** (또는 `Cmd + ,`)
3. **Advanced** 탭 클릭
4. ✅ **"Show Develop menu in menu bar"** 체크

### 2단계: Remote Automation 허용

1. 상단 메뉴바에서 **Develop** 메뉴 클릭
2. ✅ **"Allow Remote Automation"** 체크

### 3단계: safaridriver 활성화 (macOS만 해당)

터미널에서 다음 명령어 실행:

```bash
sudo safaridriver --enable
```

비밀번호를 입력하면 Safari WebDriver가 활성화됩니다.

## CiteAgent 설정

### config.yaml 수정

`config.yaml` 파일을 열고 브라우저 타입을 `safari`로 변경:

```yaml
# Browser Settings
browser:
  type: "safari"  # chrome에서 safari로 변경
  debug_port: 9222  # Safari는 사용 안 함
  user_data_dir: "ChromeProfile"  # Safari는 사용 안 함
```

## 사용 방법

### Interactive 모드

```bash
python main.py --interactive
```

실행 후:
1. Safari가 자동으로 열립니다
2. Overleaf에 로그인하고 프로젝트를 엽니다
3. 터미널에서 **Enter**를 누릅니다
4. Overleaf 에디터에서 텍스트를 선택합니다
5. 터미널에서 다시 **Enter**를 누르면 처리됩니다

### Full Document 모드

```bash
python main.py --full-document
```

### File 모드 (브라우저 불필요)

```bash
python main.py --file examples/sample.tex
```

## Chrome과 Safari 비교

| 특징 | Chrome | Safari |
|------|--------|--------|
| **설정 복잡도** | 중간 (디버깅 모드 실행) | 쉬움 (설정만 변경) |
| **세션 유지** | ✅ 디버깅 모드로 기존 세션 연결 | ❌ 매번 새 창 열림 |
| **로그인 상태** | ✅ 유지됨 | ❌ 매번 로그인 필요 (선택사항) |
| **자동 실행** | ❌ 수동으로 디버깅 모드 실행 | ✅ 자동으로 Safari 열림 |
| **macOS 통합** | 보통 | ✅ 우수 (네이티브) |

## 장단점

### Safari 장점
- ✅ 설정이 간단함 (최초 1회만)
- ✅ 자동으로 브라우저가 열림
- ✅ macOS와 잘 통합됨
- ✅ 디버깅 모드로 Chrome 실행할 필요 없음

### Safari 단점
- ❌ 매번 새 Safari 창이 열림
- ❌ 로그인 상태가 유지되지 않을 수 있음 (쿠키 설정에 따라)
- ❌ Chrome보다 Selenium 호환성이 낮음

### Chrome 장점
- ✅ 기존 세션에 연결 (로그인 유지)
- ✅ Selenium 호환성 우수
- ✅ 더 많은 자동화 옵션

### Chrome 단점
- ❌ 디버깅 모드로 실행 필요
- ❌ 설정이 조금 더 복잡함

## 추천 사용 시나리오

### Safari를 사용하세요:
- macOS를 사용하고 있고
- 간단한 설정을 원하며
- 매번 로그인해도 괜찮다면

### Chrome을 사용하세요:
- 로그인 상태를 유지하고 싶고
- 기존 브라우저 세션을 사용하고 싶으며
- 더 많은 제어가 필요하다면

## 문제 해결

### "Safari could not connect"

**해결책**:
1. Safari Preferences → Advanced → "Show Develop menu" 체크 확인
2. Develop → "Allow Remote Automation" 체크 확인
3. 터미널에서 실행: `sudo safaridriver --enable`

### "Permission denied"

**해결책**:
```bash
sudo safaridriver --enable
```
비밀번호를 입력하세요.

### Safari가 열리지 않음

**해결책**:
1. Safari를 수동으로 열어보세요
2. 다른 Safari 창이 열려있으면 모두 닫으세요
3. CiteAgent를 다시 실행하세요

### 텍스트가 업데이트되지 않음

**해결책**:
1. Overleaf 페이지를 새로고침하세요
2. `.tex` 파일이 에디터에 열려있는지 확인하세요
3. JavaScript 에러가 있는지 Safari Web Inspector로 확인하세요

## Chrome으로 다시 전환하기

Safari에서 Chrome으로 돌아가려면:

1. `config.yaml` 수정:
```yaml
browser:
  type: "chrome"  # safari에서 chrome으로 변경
```

2. Chrome 디버깅 모드 실행:
```bash
./start_chrome.sh
```

3. CiteAgent 실행:
```bash
python main.py --interactive
```

## 예시 워크플로우

### Safari 사용 시

```bash
# 1. Safari 설정 (최초 1회만)
# Safari → Preferences → Advanced → Show Develop menu 체크
# Develop → Allow Remote Automation 체크
sudo safaridriver --enable

# 2. config.yaml에서 browser.type을 "safari"로 설정

# 3. CiteAgent 실행
python main.py --interactive

# 4. Safari가 자동으로 열림

# 5. Overleaf 로그인 및 프로젝트 열기

# 6. 터미널에서 Enter

# 7. 텍스트 선택 후 작업
```

---

**팁**: Safari와 Chrome을 상황에 따라 번갈아 사용할 수 있습니다. `config.yaml`의 `browser.type`만 변경하면 됩니다!
