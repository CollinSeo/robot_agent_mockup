# Robot Agent Mockup Dashboard

Streamlit dashboard for reviewing robot patrol agent outputs in one web app.
The app currently provides three dashboard tabs:

- Change Detection Agent
- Gauge Detection Agent
- Water Leak Detection Agent

## Runtime Environment

The project was developed and verified with:

- OS: Windows
- Python: `3.11.9`
- Streamlit: `1.56.0`
- Pandas: `2.3.3`

Python package versions are pinned in [requirements.txt](requirements.txt).
No separate `ffmpeg` installation is required. The Water Leak tab captures the
target video frame in the browser using HTML5 video and canvas.

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
`- test_video_wl/
```

## Setup

### 1. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py --server.port 8501
```

Open:

```text
http://localhost:8501
```

## Implemented Features

### Common UI

- Single Streamlit app
- Tab switching between agents
- Shared sidebar summary
- FAB, point, and keyword filters
- Selectable case table
- Selected case detail panel
- Agent-level metrics

### Change Detection Agent

Data:

- CSV: `output_table.csv`
- Image folder: `test_images/`

Required columns:

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

Features:

- Shows visual change cases
- Displays reference image, current image, and diff visualization
- Supports main image selection
- Shows abnormal type, report, analysis log, and action guide

### Gauge Detection Agent

Data:

- CSV: `output_table_gauge.csv`
- Image folder: `test_images_gauge/`

Required columns:

```text
fab
point
time
type
abnormal_type
analysis_log
img_path
```

Features:

- Shows gauge inspection cases
- Provides Gauge Type filter
- Displays gauge image
- Shows normal/abnormal judgement and analysis log
- Provides a simple action guide

### Water Leak Detection Agent

Data:

- CSV: `output_table_wl.csv`
- Video folder: `test_video_wl/`

Required columns:

```text
fab
point
time
leak_detection_time_sec
video_path
```

Features:

- Shows water leak detection cases
- Plays the selected patrol video in the dashboard
- Uses `leak_detection_time_sec` to seek to the detected timestamp
- Captures and displays the frame in the browser with HTML5 canvas
- Does not require `ffmpeg` or any external video-processing binary
- Automatically maps the CSV typo `test_vido_wl` to `test_video_wl`
- Adds a generated `abnormal_type` value of `water leak` at load time

## Data Path Handling

CSV paths are interpreted relative to the project root.

Examples:

```text
./test_images_gauge/digi_img.jpg
./test_video_wl/wl_video.mp4
```

For image paths without an extension, the app tries:

```text
.png, .jpeg, .jpg, .webp
```

For video paths without an extension, the app tries:

```text
.mp4, .mov, .MOV
```

## Verification Commands

Syntax check:

```bash
python -m py_compile app.py
```

Dependency check:

```bash
python -m pip install --dry-run -r requirements.txt
```

Run check:

```bash
streamlit run app.py --server.port 8501
```

## Notes

- `requirements.txt` only manages Python dependencies.
- Water Leak frame preview is generated client-side in the browser.
- The app uses `test_video_wl/wl_video.mp4` for the Water Leak tab.
