# Robot Agent Mockup Dashboard

로봇 패트롤 결과를 한 화면에서 확인하기 위한 Streamlit 기반 mockup UI입니다.
현재 하나의 웹 앱에서 세 가지 agent 결과를 탭으로 전환해 확인할 수 있습니다.

- Change Detection Agent: 패트롤 이미지 기반 이상 변경 판단
- Gauge Detection Agent: 게이지 이미지 기반 정상/이상 판단
- Water Leak Detection Agent: 패트롤 영상 기반 누수 감지 및 감지 시점 프레임 확인

## Runtime Environment

현재 개발 및 검증에 사용한 환경입니다.

- OS: Windows
- Python: `3.11.9`
- Streamlit: `1.56.0`
- Pandas: `2.3.3`
- ffmpeg: `8.1.1-full_build-www.gyan.dev`

Python 패키지는 [requirements.txt](requirements.txt)에 고정되어 있습니다. 이 파일에는 앱에서 직접 사용하는 `streamlit`, `pandas`와 Streamlit 실행에 필요한 주요 하위 의존성 버전이 포함되어 있습니다.
Water Leak Agent의 감지 프레임 추출 기능은 Python 패키지가 아닌 시스템 실행 파일 `ffmpeg`를 사용합니다.

## Project Structure

```text
robot_agent_mockup/
|- app.py
|- requirements.txt
|- README.md
|- output_table.csv
|- output_table_gauge.csv
|- output_table_wl.csv
|- test_images/
|- test_images_gauge/
|- test_video_wl/
`- .wl_frames/              # 자동 생성되는 누수 감지 프레임 캐시
```

`.wl_frames/`는 앱 실행 중 자동 생성되는 캐시 폴더이며 git 추적 대상에서 제외되어 있습니다.

## Setup

### 1. Python 가상환경 생성

Windows PowerShell 기준:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

macOS/Linux 기준:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. ffmpeg 설치

Water Leak Agent에서 `leak_detection_time_sec` 시점의 프레임 이미지를 추출하려면 `ffmpeg`가 필요합니다.

Windows에서 winget 사용 시:

```powershell
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
```

설치 후 새 터미널에서 아래 명령이 동작해야 합니다.

```bash
ffmpeg -version
```

앱은 Windows winget 기본 설치 경로의 Gyan FFmpeg도 자동으로 탐색합니다. 그래도 가장 안정적인 방식은 `ffmpeg`가 PATH에 잡히도록 새 터미널을 여는 것입니다.

## Run

```bash
streamlit run app.py --server.port 8501
```

브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8501
```

같은 주소에서 상단 탭으로 세 agent 대시보드를 전환할 수 있습니다.

## Implemented Features

### Common Dashboard

- Streamlit 단일 앱으로 통합
- 탭 기반 agent 전환
- 공통 사이드바 요약
- FAB, point, keyword 기반 필터
- 케이스 테이블 선택
- 선택 케이스 상세 패널 표시
- agent별 전체 케이스 수, 표시 케이스 수, 지점 수, 이상 케이스 수 표시

### Change Detection Agent

연결 데이터:

- CSV: `output_table.csv`
- 이미지 폴더: `test_images/`

필수 컬럼:

```text
fab
point
time
abnormal_type
abnormal_report
analysis_log
action_guide
reference_image_path
current_image_path
diff_visualization_path
```

기능:

- 이상 변경 케이스 목록 표시
- 기준 이미지, 현재 이미지, Diff 시각화 표시
- 대표 이미지 라디오 선택
- 이상 유형, 판단 근거, 분석 로그, 조치 사항 표시

### Gauge Detection Agent

연결 데이터:

- CSV: `output_table_gauge.csv`
- 이미지 폴더: `test_images_gauge/`

필수 컬럼:

```text
fab
point
time
type
abnormal_type
analysis_log
img_path
```

기능:

- 게이지 케이스 목록 표시
- Gauge Type 필터 제공
- 게이지 이미지 표시
- 정상/이상 판정 표시
- 분석 로그 및 조치 가이드 표시

### Water Leak Detection Agent

연결 데이터:

- CSV: `output_table_wl.csv`
- 비디오 폴더: `test_video_wl/`

필수 컬럼:

```text
fab
point
time
leak_detection_time_sec
video_path
```

기능:

- 누수 감지 케이스 목록 표시
- 선택 케이스의 비디오 재생
- `leak_detection_time_sec` 초에 해당하는 프레임을 `ffmpeg`로 추출
- 추출 프레임 이미지를 대시보드에 표시
- 추출된 프레임은 `.wl_frames/`에 캐시
- CSV의 `video_path`에 `test_vido_wl` 오타가 있어도 앱에서 `test_video_wl`로 자동 보정
- Water Leak CSV에는 별도 `abnormal_type` 컬럼이 없으므로 앱 로딩 단계에서 `water leak` 판정값을 자동 생성

## Data Path Handling

앱은 CSV 안의 상대 경로를 프로젝트 루트 기준으로 해석합니다.

예:

```text
./test_images_gauge/digi_img.jpg
./test_video_wl/wl_video.mp4
```

이미지 경로에 확장자가 없으면 아래 확장자를 순서대로 탐색합니다.

```text
.png, .jpeg, .jpg, .webp
```

비디오 경로에 확장자가 없으면 아래 확장자를 순서대로 탐색합니다.

```text
.mp4, .mov, .MOV
```

## Verification Commands

문법 확인:

```bash
python -m py_compile app.py
```

앱 실행:

```bash
streamlit run app.py --server.port 8501
```

ffmpeg 확인:

```bash
ffmpeg -version
```

## Notes

- `requirements.txt`는 Python 패키지만 관리합니다.
- `ffmpeg`는 별도 시스템 의존성이므로 새 컴퓨터에 반드시 설치해야 Water Leak 프레임 추출이 동작합니다.
- 원본 MOV 파일은 없어도 현재 Water Leak Agent는 `test_video_wl/wl_video.mp4`를 사용합니다.
