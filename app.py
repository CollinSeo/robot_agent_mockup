from dataclasses import dataclass
from html import escape
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
ALL_OPTION = "All"
FRAME_CACHE_DIR = ROOT / ".wl_frames"


@dataclass(frozen=True)
class AgentConfig:
    key: str
    tab_label: str
    sidebar_label: str
    eyebrow: str
    title: str
    subtitle: str
    csv_path: Path
    required_columns: list[str]
    display_columns: list[str]
    media_mode: str
    point_metric_label: str
    abnormal_metric_label: str


CHANGE_AGENT = AgentConfig(
    key="change",
    tab_label="Change Detection",
    sidebar_label="Change Agent",
    eyebrow="Agent 1",
    title="Visual Change Detection Results",
    subtitle=(
        "Review patrol-image change detection results. Select a case to compare the "
        "reference image, current image, diff visualization, and detailed analysis."
    ),
    csv_path=ROOT / "output_table.csv",
    required_columns=[
        "fab",
        "point",
        "time",
        "abnormal_type",
        "abnormal_report",
        "analysis_log",
        "action_guide",
        "reference_image_path",
        "current_image_path",
        "diff_visualization_path",
    ],
    display_columns=[
        "case_no",
        "fab",
        "point",
        "time",
        "abnormal_type",
        "abnormal_report",
        "analysis_log",
        "action_guide",
    ],
    media_mode="comparison",
    point_metric_label="Inspection Points",
    abnormal_metric_label="Abnormal Cases",
)

GAUGE_AGENT = AgentConfig(
    key="gauge",
    tab_label="Gauge Detection",
    sidebar_label="Gauge Agent",
    eyebrow="Agent 2",
    title="Gauge Abnormality Detection Results",
    subtitle=(
        "Review gauge image analysis results. Select a case to inspect the gauge type, "
        "normal/abnormal judgement, image, and analysis log."
    ),
    csv_path=ROOT / "output_table_gauge.csv",
    required_columns=[
        "fab",
        "point",
        "time",
        "type",
        "abnormal_type",
        "analysis_log",
        "img_path",
    ],
    display_columns=[
        "case_no",
        "fab",
        "point",
        "time",
        "type",
        "abnormal_type",
        "analysis_log",
    ],
    media_mode="single",
    point_metric_label="Gauge Points",
    abnormal_metric_label="Abnormal Gauges",
)

WATER_LEAK_AGENT = AgentConfig(
    key="water_leak",
    tab_label="Water Leak Detection",
    sidebar_label="Water Leak Agent",
    eyebrow="Agent 3",
    title="Water Leak Detection Results",
    subtitle=(
        "Review leak detection results from patrol video. Select a case to play the "
        "source video and inspect the frame at the detected leak timestamp."
    ),
    csv_path=ROOT / "output_table_wl.csv",
    required_columns=[
        "fab",
        "point",
        "time",
        "leak_detection_time_sec",
        "video_path",
    ],
    display_columns=[
        "case_no",
        "fab",
        "point",
        "time",
        "leak_detection_time_sec",
        "abnormal_type",
        "video_path",
    ],
    media_mode="video",
    point_metric_label="Video Points",
    abnormal_metric_label="Leak Cases",
)

AGENTS = [CHANGE_AGENT, GAUGE_AGENT, WATER_LEAK_AGENT]


st.set_page_config(
    page_title="Robot Agent Mockup",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f7fb;
            --ink: #13202e;
            --muted: #66778c;
            --line: #d9e1eb;
            --panel: #ffffff;
            --brand: #1267d8;
            --brand-soft: #e8f1ff;
            --danger: #b91c1c;
            --danger-soft: #fee2e2;
            --ok: #15803d;
            --ok-soft: #dcfce7;
            --warning-soft: #fffbeb;
        }

        .stApp {
            background: var(--bg);
            color: var(--ink);
        }

        header[data-testid="stHeader"] {
            height: 2.75rem;
            background: transparent;
            border: 0;
            pointer-events: none;
        }

        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] [role="button"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"] {
            pointer-events: auto !important;
        }

        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stDeployButton,
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        header[data-testid="stHeader"] [data-testid="stBaseButton-header"],
        header[data-testid="stHeader"] [data-testid="stMainMenuButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        header[data-testid="stHeader"] [data-testid="stBaseButton-headerNoPadding"] {
            display: flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(18, 32, 46, 0.14);
        }

        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            position: fixed !important;
            top: 0.55rem !important;
            left: 0.7rem !important;
            z-index: 999999 !important;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(18, 32, 46, 0.14);
            pointer-events: auto !important;
        }

        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] {
            color: var(--ink) !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: flex !important;
            visibility: visible !important;
            justify-content: flex-end;
            padding-right: 8px;
        }

        [data-testid="stSidebarCollapseButton"] button {
            display: flex !important;
            visibility: visible !important;
            width: 32px;
            height: 32px;
            border: 1px solid rgba(255,255,255,.22);
            border-radius: 999px;
            background: rgba(255,255,255,.10);
            color: #ffffff !important;
            pointer-events: auto !important;
        }

        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
            color: #ffffff !important;
        }

        .block-container {
            max-width: 1560px;
            padding-top: 2.9rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #0f1b2a;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] .stCaptionContainer,
        [data-testid="stSidebar"] small {
            color: #bac7d7 !important;
        }

        .hero {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px 20px;
            box-shadow: 0 16px 42px rgba(18, 32, 46, 0.08);
            margin-bottom: 16px;
        }

        .eyebrow {
            color: var(--brand);
            font-size: 12px;
            font-weight: 850;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .title-row {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }

        .title {
            color: var(--ink);
            font-size: 28px;
            font-weight: 850;
            line-height: 1.22;
            margin: 0;
        }

        .subtitle {
            color: var(--muted);
            font-size: 14px;
            line-height: 1.55;
            margin-top: 8px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 8px 12px;
            background: var(--danger-soft);
            color: var(--danger);
            font-size: 13px;
            font-weight: 850;
            white-space: nowrap;
        }

        .metric-card {
            background: rgba(255,255,255,.08);
            border: 1px solid rgba(255,255,255,.12);
            border-radius: 8px;
            padding: 12px;
        }

        .metric-card strong {
            display: block;
            color: #fff;
            font-size: 24px;
            line-height: 1;
        }

        .metric-card span {
            display: block;
            color: #bac7d7;
            font-size: 12px;
            margin-top: 5px;
        }

        .section-title {
            color: var(--ink);
            font-size: 18px;
            font-weight: 850;
            margin: 2px 0 8px;
        }

        .panel-title {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: center;
            margin-bottom: 10px;
        }

        .panel-title h3 {
            margin: 0;
            color: var(--ink);
            font-size: 18px;
        }

        .panel-title p,
        .muted {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.5;
            margin: 0;
        }

        .case-row-current {
            border: 1px solid #9cc3ff;
            background: var(--brand-soft);
            color: var(--brand);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 6px 10px;
            margin: 0 6px 6px 0;
            background: #eef3f8;
            color: #344256;
            font-size: 12px;
            font-weight: 850;
        }

        .chip.danger {
            background: var(--danger-soft);
            color: var(--danger);
        }

        .chip.ok {
            background: var(--ok-soft);
            color: var(--ok);
        }

        .result-box {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
            background: #fbfdff;
            min-height: 112px;
        }

        .result-box.action {
            border-color: #fde68a;
            background: var(--warning-soft);
        }

        .result-label {
            color: var(--muted);
            font-size: 13px;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .result-text {
            color: var(--ink);
            font-size: 15px;
            line-height: 1.58;
        }

        div[data-testid="stImageContainer"] img {
            border-radius: 8px;
            border: 1px solid var(--line);
            background: #0b1220;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_results(agent_key: str) -> pd.DataFrame:
    config = next(agent for agent in AGENTS if agent.key == agent_key)
    df = pd.read_csv(config.csv_path, encoding="utf-8")
    missing_columns = [column for column in config.required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing_columns)}")

    df = df.copy()
    if agent_key == "water_leak":
        df["abnormal_type"] = "water leak"
        df["analysis_log"] = df["leak_detection_time_sec"].apply(
            lambda sec: f"Leak detected at {sec} sec in the patrol video."
        )
        df["action_guide"] = "Inspect the detected area and verify leak source immediately."

    df["case_no"] = range(1, len(df) + 1)
    df["case_id"] = (
        df["fab"].astype(str)
        + " / "
        + df["point"].astype(str)
        + " / "
        + df["time"].astype(str)
    )
    return df


def normalize_path_text(raw_path: object) -> str:
    path_text = str(raw_path).strip().replace("\\", "/")
    if path_text.startswith("./"):
        path_text = path_text[2:]
    return path_text


def resolve_file_path(raw_path: object, suffixes: tuple[str, ...] = ()) -> Path:
    path_text = normalize_path_text(raw_path)
    candidates = [ROOT / path_text]

    if "test_vido_wl" in path_text:
        candidates.append(ROOT / path_text.replace("test_vido_wl", "test_video_wl"))

    for candidate in candidates:
        if candidate.exists():
            return candidate
        if not candidate.suffix:
            for suffix in suffixes:
                with_suffix = candidate.with_suffix(suffix)
                if with_suffix.exists():
                    return with_suffix

    candidate = candidates[-1]
    if candidate.suffix or not suffixes:
        return candidate
    return candidate.with_suffix(suffixes[0])


def resolve_image_path(raw_path: object) -> Path:
    return resolve_file_path(raw_path, (".png", ".jpeg", ".jpg", ".webp"))


def resolve_video_path(raw_path: object) -> Path:
    return resolve_file_path(raw_path, (".mp4", ".mov", ".MOV"))


def find_ffmpeg_exe() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_root.exists():
        matches = sorted(winget_root.glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe"))
        if matches:
            return str(matches[-1])
    return None


@st.cache_data(show_spinner=False)
def extract_video_frame(video_path_text: str, seconds: float, case_no: int) -> tuple[str | None, str | None]:
    video_path = resolve_video_path(video_path_text)
    if not video_path.exists():
        return None, f"Video file was not found: {video_path}"

    ffmpeg = find_ffmpeg_exe()
    if not ffmpeg:
        return None, "ffmpeg was not found. Install ffmpeg to extract leak frames."

    FRAME_CACHE_DIR.mkdir(exist_ok=True)
    safe_stem = video_path.stem.replace(" ", "_")
    frame_path = FRAME_CACHE_DIR / f"{safe_stem}_case_{case_no:03d}_{float(seconds):.2f}s.jpg"
    if frame_path.exists():
        return str(frame_path), None

    command = [
        ffmpeg,
        "-y",
        "-ss",
        str(seconds),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(frame_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not frame_path.exists():
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "Unknown ffmpeg error"
        return None, f"Could not extract frame at {seconds} sec: {detail}"
    return str(frame_path), None


def safe_text(value: object) -> str:
    if pd.isna(value):
        return "-"
    return escape(str(value))


def is_abnormal(value: object) -> bool:
    text = str(value).strip().lower()
    return text not in {"", "-", "normal", "ok", "정상"}


def render_sidebar_metric(label: str, value: int) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <strong>{value}</strong>
            <span>{safe_text(label)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_box(label: str, text: object, action: bool = False) -> None:
    action_class = " action" if action else ""
    st.markdown(
        f"""
        <div class="result-box{action_class}">
            <div class="result-label">{safe_text(label)}</div>
            <div class="result-text">{safe_text(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(config: AgentConfig, total_count: int, filtered_count: int) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{safe_text(config.eyebrow)}</div>
            <div class="title-row">
                <div>
                    <div class="title">{safe_text(config.title)}</div>
                    <div class="subtitle">{safe_text(config.subtitle)}</div>
                </div>
                <div class="status-badge">Showing {filtered_count} / {total_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chips(row: pd.Series) -> None:
    abnormal_class = "danger" if is_abnormal(row["abnormal_type"]) else "ok"
    optional_chips = ""
    if "type" in row:
        optional_chips += f'<span class="chip">{safe_text(row["type"])}</span>'
    if "leak_detection_time_sec" in row:
        optional_chips += f'<span class="chip">{safe_text(row["leak_detection_time_sec"])} sec</span>'

    st.markdown(
        f"""
        <span class="chip">Case {int(row["case_no"]):02d}</span>
        <span class="chip">{safe_text(row["fab"])}</span>
        <span class="chip">{safe_text(row["point"])}</span>
        <span class="chip">{safe_text(row["time"])}</span>
        {optional_chips}
        <span class="chip {abnormal_class}">{safe_text(row["abnormal_type"])}</span>
        """,
        unsafe_allow_html=True,
    )


def filter_results(
    df: pd.DataFrame,
    selected_fab: str,
    selected_point: str,
    selected_type: str,
    keyword: str,
) -> pd.DataFrame:
    filtered = df.copy()
    if selected_fab != ALL_OPTION:
        filtered = filtered[filtered["fab"].astype(str) == selected_fab]
    if selected_point != ALL_OPTION:
        filtered = filtered[filtered["point"].astype(str) == selected_point]
    if "type" in filtered.columns and selected_type != ALL_OPTION:
        filtered = filtered[filtered["type"].astype(str) == selected_type]
    if keyword.strip():
        keyword_lower = keyword.strip().lower()
        search_columns = [
            column
            for column in [
                "fab",
                "point",
                "time",
                "type",
                "abnormal_type",
                "abnormal_report",
                "analysis_log",
                "action_guide",
                "leak_detection_time_sec",
                "video_path",
            ]
            if column in filtered.columns
        ]
        search_text = filtered[search_columns].astype(str).agg(" ".join, axis=1).str.lower()
        filtered = filtered[search_text.str.contains(keyword_lower, regex=False)]
    return filtered


def render_filters(df: pd.DataFrame, config: AgentConfig) -> tuple[str, str, str, str]:
    with st.container(border=True):
        st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)
        if "type" in df.columns:
            cols = st.columns([1, 1, 1, 2], gap="medium")
        else:
            cols = st.columns([1, 1, 2], gap="medium")

        with cols[0]:
            fab_options = [ALL_OPTION] + sorted(df["fab"].astype(str).unique().tolist())
            selected_fab = st.selectbox("FAB", fab_options, key=f"{config.key}_fab")

        point_source = df if selected_fab == ALL_OPTION else df[df["fab"].astype(str) == selected_fab]
        with cols[1]:
            point_options = [ALL_OPTION] + sorted(point_source["point"].astype(str).unique().tolist())
            selected_point = st.selectbox("Point", point_options, key=f"{config.key}_point")

        selected_type = ALL_OPTION
        keyword_col_index = 2
        if "type" in df.columns:
            type_source = point_source
            if selected_point != ALL_OPTION:
                type_source = type_source[type_source["point"].astype(str) == selected_point]
            with cols[2]:
                type_options = [ALL_OPTION] + sorted(type_source["type"].astype(str).unique().tolist())
                selected_type = st.selectbox("Gauge Type", type_options, key=f"{config.key}_type")
            keyword_col_index = 3

        with cols[keyword_col_index]:
            keyword = st.text_input(
                "Search",
                placeholder="time, type, judgement, log, video path",
                key=f"{config.key}_keyword",
            )

    return selected_fab, selected_point, selected_type, keyword


def render_case_table(filtered: pd.DataFrame, config: AgentConfig) -> pd.Series:
    filtered = filtered.reset_index(drop=True)
    state_key = f"{config.key}_selected_case_no"
    visible_case_numbers = set(filtered["case_no"].astype(int).tolist())
    if state_key not in st.session_state or int(st.session_state[state_key]) not in visible_case_numbers:
        st.session_state[state_key] = int(filtered.iloc[0]["case_no"])

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="panel-title">
                <div>
                    <h3>{safe_text(config.tab_label)} Cases</h3>
                    <p>Select a row to inspect the media and judgement details below.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        table_df = filtered[config.display_columns].reset_index(drop=True)
        selected_index = int(
            filtered.index[filtered["case_no"].astype(int) == int(st.session_state[state_key])][0]
        )
        case_key_text = "_".join(filtered["case_no"].astype(str).tolist())
        table_event = st.dataframe(
            table_df,
            width="stretch",
            hide_index=True,
            height=225,
            on_select="rerun",
            selection_mode="single-row-required",
            selection_default={"selection": {"rows": [selected_index]}},
            row_height=30,
            key=f"{config.key}_case_table_{case_key_text}",
            column_config={
                "case_no": st.column_config.NumberColumn("Case", width="small"),
                "fab": st.column_config.TextColumn("FAB", width="small"),
                "point": st.column_config.TextColumn("Point", width="medium"),
                "time": st.column_config.TextColumn("Time", width="small"),
                "type": st.column_config.TextColumn("Gauge Type", width="small"),
                "abnormal_type": st.column_config.TextColumn("Judgement", width="medium"),
                "abnormal_report": st.column_config.TextColumn("Report", width="large"),
                "analysis_log": st.column_config.TextColumn("Analysis Log", width="large"),
                "action_guide": st.column_config.TextColumn("Action Guide", width="large"),
                "leak_detection_time_sec": st.column_config.NumberColumn("Leak Time (sec)", width="small"),
                "video_path": st.column_config.TextColumn("Video", width="large"),
            },
        )

        selected_rows = table_event.selection.rows
        if selected_rows:
            selected_index = selected_rows[0]
            st.session_state[state_key] = int(filtered.iloc[selected_index]["case_no"])

        selected_row = filtered[filtered["case_no"].astype(int) == int(st.session_state[state_key])].iloc[0]
        st.markdown(
            f"""
            <div class="case-row-current">
                Selected Case {int(selected_row["case_no"]):02d} ·
                {safe_text(selected_row["fab"])} · {safe_text(selected_row["point"])} ·
                {safe_text(selected_row["time"])} · {safe_text(selected_row["abnormal_type"])}
            </div>
            """,
            unsafe_allow_html=True,
        )
    return selected_row


def render_comparison_images(row: pd.Series, config: AgentConfig) -> None:
    image_paths = {
        "Reference Image": resolve_image_path(row["reference_image_path"]),
        "Current Image": resolve_image_path(row["current_image_path"]),
        "Diff Visualization": resolve_image_path(row["diff_visualization_path"]),
    }
    selected_image_label = st.radio(
        "Main image",
        list(image_paths.keys()),
        index=2,
        horizontal=True,
        key=f"{config.key}_image_radio",
    )
    selected_path = image_paths[selected_image_label]
    if selected_path.exists():
        st.image(
            str(selected_path),
            caption=f"{selected_image_label} · {selected_path.name}",
            use_container_width=True,
        )
    else:
        st.error(f"{selected_image_label} file was not found: {selected_path}")

    thumb_cols = st.columns(3)
    for col, (label, path) in zip(thumb_cols, image_paths.items()):
        with col:
            if path.exists():
                st.image(str(path), caption=label, use_container_width=True)
            else:
                st.warning(f"{label} missing")


def render_single_image(row: pd.Series) -> None:
    image_path = resolve_image_path(row["img_path"])
    if image_path.exists():
        st.image(str(image_path), caption=image_path.name, use_container_width=True)
    else:
        st.error(f"Gauge image file was not found: {image_path}")


def render_video_case(row: pd.Series) -> None:
    video_path = resolve_video_path(row["video_path"])
    leak_time = float(row["leak_detection_time_sec"])

    st.markdown("**Patrol Video**")
    if video_path.exists():
        st.video(str(video_path))
    else:
        st.error(f"Video file was not found: {video_path}")

    st.markdown(f"**Detected Frame at {leak_time:g} sec**")
    frame_path, error = extract_video_frame(str(row["video_path"]), leak_time, int(row["case_no"]))
    if frame_path:
        st.image(frame_path, caption=f"Leak detection frame · {leak_time:g} sec", use_container_width=True)
    else:
        st.warning(error)


def render_selected_case(row: pd.Series, config: AgentConfig) -> None:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="panel-title">
                <div>
                    <h3>Selected Case Detail</h3>
                    <p>{safe_text(row["case_id"])}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_chips(row)

        media_col, detail_col = st.columns([1.45, 1], gap="large")
        with media_col:
            if config.media_mode == "comparison":
                render_comparison_images(row, config)
            elif config.media_mode == "single":
                render_single_image(row)
            else:
                render_video_case(row)

        with detail_col:
            if config.media_mode == "comparison":
                render_result_box("Abnormal Type", row["abnormal_type"])
                st.write("")
                render_result_box("Report", row["abnormal_report"])
                st.write("")
                render_result_box("Analysis Log", row["analysis_log"])
                st.write("")
                render_result_box("Action Guide", row["action_guide"], action=True)
            elif config.media_mode == "single":
                render_result_box("Gauge Type", row["type"])
                st.write("")
                render_result_box("Judgement", row["abnormal_type"])
                st.write("")
                render_result_box("Analysis Log", row["analysis_log"])
                st.write("")
                guide = "Inspect the gauge state and verify the threshold setting."
                if not is_abnormal(row["abnormal_type"]):
                    guide = "Normal judgement. Keep the record for routine patrol history."
                render_result_box("Action Guide", guide, action=True)
            else:
                render_result_box("Leak Detection Time", f"{row['leak_detection_time_sec']} sec")
                st.write("")
                render_result_box("Judgement", row["abnormal_type"])
                st.write("")
                render_result_box("Analysis Log", row["analysis_log"])
                st.write("")
                render_result_box("Action Guide", row["action_guide"], action=True)


def render_dashboard(config: AgentConfig) -> pd.DataFrame:
    try:
        df = load_results(config.key)
    except Exception as exc:
        st.error(f"Could not read {config.csv_path.name}: {exc}")
        st.stop()

    selected_fab, selected_point, selected_type, keyword = render_filters(df, config)
    filtered = filter_results(df, selected_fab, selected_point, selected_type, keyword)

    render_header(config, total_count=len(df), filtered_count=len(filtered))

    if filtered.empty:
        st.warning("No cases match the current filters.")
        return df

    abnormal_count = int(df["abnormal_type"].map(is_abnormal).sum())
    top_cols = st.columns(4)
    top_cols[0].metric("Visible", len(filtered))
    top_cols[1].metric("Total Cases", len(df))
    top_cols[2].metric(config.point_metric_label, df[["fab", "point"]].drop_duplicates().shape[0])
    top_cols[3].metric(config.abnormal_metric_label, abnormal_count)

    selected_row = render_case_table(filtered, config)
    st.write("")
    render_selected_case(selected_row, config)
    return df


def render_sidebar(all_data: dict[str, pd.DataFrame | None]) -> None:
    with st.sidebar:
        st.markdown("## Robot Agent Dashboard")
        st.caption(
            "Switch between visual change, gauge, and water leak agents from one dashboard."
        )

        for config in AGENTS:
            df = all_data.get(config.key)
            if df is None:
                continue

            st.markdown(f"### {config.sidebar_label}")
            metric_cols = st.columns(2)
            with metric_cols[0]:
                render_sidebar_metric("Total Cases", len(df))
            with metric_cols[1]:
                render_sidebar_metric(
                    config.point_metric_label,
                    df[["fab", "point"]].drop_duplicates().shape[0],
                )
            st.write("")


def main() -> None:
    inject_style()

    loaded_data: dict[str, pd.DataFrame | None] = {}
    for config in AGENTS:
        try:
            loaded_data[config.key] = load_results(config.key)
        except Exception:
            loaded_data[config.key] = None
    render_sidebar(loaded_data)

    tabs = st.tabs([agent.tab_label for agent in AGENTS])
    for tab, config in zip(tabs, AGENTS):
        with tab:
            render_dashboard(config)


if __name__ == "__main__":
    main()
