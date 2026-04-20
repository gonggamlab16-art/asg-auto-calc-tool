# 건축 도면 기반 자동 물량 산출기 (Streamlit)

건축 도면(CAD) 데이터를 기반으로 항목별 물량(벽/창호/바닥/천장 등)을 자동 집계하고, 엑셀 산출근거서를 생성하는 Python 웹 앱입니다.

> 로컬 실행 방법은 본 문서의 **2) 가상환경 설정**, **3) 의존성 설치**, **4) 앱 실행 방법**을 순서대로 따라 진행하세요.

---

## 1) 필수 요구사항

### 공통
- **Python 3.10 이상** (권장: 3.11)
- **pip 최신 버전**

버전 확인 명령어:

```bash
python --version
pip --version
```

> 환경에 따라 `python` 대신 `python3`를 사용해야 할 수 있습니다.

---

## 2) 가상환경 설정 방법 (venv)

프로젝트 루트(현재 폴더)에서 아래 명령어를 실행하세요.

### 가상환경 생성
```bash
python -m venv .venv
```

### 가상환경 활성화
- **Windows (PowerShell)**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS / Linux (bash/zsh)**
  ```bash
  source .venv/bin/activate
  ```

활성화되면 프롬프트 앞에 `(.venv)`가 표시됩니다.

---

## 3) 의존성 설치 명령어

가상환경 활성화 후 아래 명령어를 실행하세요.

```bash
pip install -r requirements.txt
```

설치 확인(선택):

```bash
pip list
```

---

## 4) 앱 실행 방법

```bash
streamlit run app.py
```

실행 후 터미널에 표시되는 로컬 주소(일반적으로 `http://localhost:8501`)를 브라우저에서 열면 됩니다.

종료는 터미널에서 `Ctrl + C`를 누르세요.

---

## 5) 테스트용 샘플 DXF 파일 만드는 방법

아래 스크립트로 간단한 샘플 도면(`sample_test.dxf`)을 생성할 수 있습니다.

### 5-1. 샘플 생성 스크립트 파일 만들기
프로젝트 루트에 `make_sample_dxf.py` 파일을 만들고 아래 내용을 붙여넣으세요.

```python
import ezdxf

# 새 DXF 문서 생성
doc = ezdxf.new("R2010")
msp = doc.modelspace()

# 벽 레이어 예시 (사각형 외곽)
doc.layers.add("A-WALL")
msp.add_lwpolyline(
    [(0, 0), (10000, 0), (10000, 8000), (0, 8000), (0, 0)],
    dxfattribs={"layer": "A-WALL"},
)

# 창호 레이어 예시 (선)
doc.layers.add("A-WINDOW")
msp.add_line((2000, 0), (3500, 0), dxfattribs={"layer": "A-WINDOW"})

# 바닥 레이어 예시 (닫힌 폴리라인)
doc.layers.add("A-FLOOR")
msp.add_lwpolyline(
    [(500, 500), (9500, 500), (9500, 7500), (500, 7500)],
    close=True,
    dxfattribs={"layer": "A-FLOOR"},
)

# 천장 레이어 예시 (닫힌 폴리라인)
doc.layers.add("A-CEILING")
msp.add_lwpolyline(
    [(1000, 1000), (9000, 1000), (9000, 7000), (1000, 7000)],
    close=True,
    dxfattribs={"layer": "A-CEILING"},
)

doc.saveas("sample_test.dxf")
print("sample_test.dxf 생성 완료")
```

### 5-2. 샘플 생성 실행
```bash
python make_sample_dxf.py
```

생성된 `sample_test.dxf`를 앱에서 업로드해 동작을 테스트할 수 있습니다.

---

## 6) 운영체제별 실행 가이드 (Windows / macOS / Linux)

## Windows
1. PowerShell 또는 CMD 실행
2. 프로젝트 폴더로 이동
3. 가상환경 생성/활성화
4. 의존성 설치
5. 앱 실행

예시(PowerShell):
```powershell
cd C:\path\to\asg-auto-calc-tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

> PowerShell 실행 정책 오류가 나면 관리자 PowerShell에서 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`를 설정한 뒤 다시 시도하세요.

## macOS
1. 터미널 실행
2. 프로젝트 폴더로 이동
3. 가상환경 생성/활성화
4. 의존성 설치
5. 앱 실행

```bash
cd /path/to/asg-auto-calc-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Linux
1. 터미널 실행
2. 프로젝트 폴더로 이동
3. 가상환경 생성/활성화
4. 의존성 설치
5. 앱 실행

```bash
cd /path/to/asg-auto-calc-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 빠른 점검 체크리스트
- [ ] `python --version` 또는 `python3 --version` 확인
- [ ] 가상환경 활성화 확인 (`(.venv)` 표시)
- [ ] `pip install -r requirements.txt` 성공
- [ ] `streamlit run app.py` 실행 후 브라우저 접속 확인
- [ ] `sample_test.dxf` 업로드 및 결과 테이블 확인
