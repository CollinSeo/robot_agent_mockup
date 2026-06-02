import base64
from dataclasses import dataclass
from datetime import timedelta
from html import escape
import json
import mimetypes
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).parent
ALL_OPTION = "All"


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

WATER_LEAK_AGENT = AgentConfig(
    key="water_leak",
    tab_label="Water Leak Detection",
    sidebar_label="Water Leak Agent",
    eyebrow="Agent 2",
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

AGENTS = [CHANGE_AGENT, WATER_LEAK_AGENT]


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

        .result-box.danger {
            border-color: #fecaca;
            background: #fef2f2;
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

        .result-box.danger .result-text {
            color: var(--danger);
            font-weight: 850;
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

    df["_time_dt"] = pd.to_datetime(df["time"], errors="coerce")
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


@st.cache_data(show_spinner=False)
def video_data_uri(video_path_text: str) -> tuple[str | None, str | None]:
    video_path = resolve_video_path(video_path_text)
    if not video_path.exists():
        return None, f"Video file was not found: {video_path}"

    mime_type = mimetypes.guess_type(video_path.name)[0] or "video/mp4"
    encoded = base64.b64encode(video_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", None


@st.cache_data(show_spinner=False)
def image_data_uri(image_path_text: str) -> tuple[str | None, str | None]:
    image_path = resolve_image_path(image_path_text)
    if not image_path.exists():
        return None, f"Image file was not found: {image_path}"

    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", None


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


def render_result_box(label: str, text: object, action: bool = False, danger: bool = False) -> None:
    classes = ["result-box"]
    if action:
        classes.append("action")
    if danger:
        classes.append("danger")
    st.markdown(
        f"""
        <div class="{' '.join(classes)}">
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


def render_zoomable_diff_image(image_path: Path, caption: str, component_key: str) -> None:
    data_uri, error = image_data_uri(str(image_path))
    if error or not data_uri:
        st.error(error or f"Diff image file was not found: {image_path}")
        return

    safe_caption = safe_text(caption)
    components.html(
        f"""
        <div class="zoom-viewer">
            <style>
                .zoom-viewer {{
                    position: relative;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: #13202e;
                    padding-bottom: 2px;
                }}
                .zoom-stage {{
                    position: relative;
                    display: block;
                    width: fit-content;
                    max-width: 100%;
                    margin: 0 auto;
                    line-height: 0;
                }}
                .zoom-image {{
                    display: block;
                    width: auto;
                    max-width: 100%;
                    max-height: 380px;
                    height: auto;
                    border: 1px solid #d9e1eb;
                    border-radius: 8px;
                    background: #0b1220;
                    box-sizing: border-box;
                    cursor: crosshair;
                }}
                .zoom-lens {{
                    position: absolute;
                    display: none;
                    width: 240px;
                    height: 240px;
                    border: 2px solid #1267d8;
                    border-radius: 8px;
                    background-repeat: no-repeat;
                    background-color: #ffffff;
                    box-shadow: 0 16px 42px rgba(18, 32, 46, 0.22);
                    pointer-events: none;
                    z-index: 10;
                }}
                .zoom-crosshair {{
                    position: absolute;
                    display: none;
                    width: 18px;
                    height: 18px;
                    border: 2px solid #1267d8;
                    border-radius: 999px;
                    transform: translate(-50%, -50%);
                    pointer-events: none;
                    z-index: 9;
                    box-shadow: 0 0 0 2px rgba(255,255,255,.85);
                }}
                .zoom-caption {{
                    color: #66778c;
                    font-size: 13px;
                    line-height: 1.3;
                    margin-top: 4px;
                }}
            </style>
            <div id="{component_key}_stage" class="zoom-stage">
                <img id="{component_key}_image" class="zoom-image" src={json.dumps(data_uri)} alt="Diff visualization" />
                <div id="{component_key}_crosshair" class="zoom-crosshair"></div>
                <div id="{component_key}_lens" class="zoom-lens"></div>
            </div>
            <div class="zoom-caption">{safe_caption} - hover over the diff image to inspect details.</div>
            <script>
                const stage = document.getElementById("{component_key}_stage");
                const image = document.getElementById("{component_key}_image");
                const lens = document.getElementById("{component_key}_lens");
                const crosshair = document.getElementById("{component_key}_crosshair");
                const zoom = 2.6;
                const lensSize = 240;
                const margin = 14;

                function updateLens(event) {{
                    const rect = image.getBoundingClientRect();
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;

                    if (x < 0 || y < 0 || x > rect.width || y > rect.height) {{
                        hideLens();
                        return;
                    }}

                    const stageRect = stage.getBoundingClientRect();
                    let left = x + margin;
                    let top = y + margin;
                    if (left + lensSize > stageRect.width) left = x - lensSize - margin;
                    if (top + lensSize > stageRect.height) top = y - lensSize - margin;
                    left = Math.max(0, Math.min(left, Math.max(stageRect.width - lensSize, 0)));
                    top = Math.max(0, Math.min(top, Math.max(stageRect.height - lensSize, 0)));

                    lens.style.display = "block";
                    lens.style.left = `${{left}}px`;
                    lens.style.top = `${{top}}px`;
                    lens.style.backgroundImage = `url(${{image.src}})`;
                    lens.style.backgroundSize = `${{rect.width * zoom}}px ${{rect.height * zoom}}px`;
                    lens.style.backgroundPosition = `${{-(x * zoom - lensSize / 2)}}px ${{-(y * zoom - lensSize / 2)}}px`;

                    crosshair.style.display = "block";
                    crosshair.style.left = `${{x}}px`;
                    crosshair.style.top = `${{y}}px`;
                }}

                function hideLens() {{
                    lens.style.display = "none";
                    crosshair.style.display = "none";
                }}

                image.addEventListener("mousemove", updateLens);
                image.addEventListener("mouseleave", hideLens);
            </script>
        </div>
        """,
        height=425,
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
    selected_time_range: tuple | None,
    keyword: str,
) -> pd.DataFrame:
    filtered = df.copy()
    if selected_fab != ALL_OPTION:
        filtered = filtered[filtered["fab"].astype(str) == selected_fab]
    if selected_point != ALL_OPTION:
        filtered = filtered[filtered["point"].astype(str) == selected_point]
    if "type" in filtered.columns and selected_type != ALL_OPTION:
        filtered = filtered[filtered["type"].astype(str) == selected_type]
    if selected_time_range and "_time_dt" in filtered.columns:
        start_time, end_time = selected_time_range
        filtered = filtered[
            filtered["_time_dt"].notna()
            & (filtered["_time_dt"] >= pd.Timestamp(start_time))
            & (filtered["_time_dt"] <= pd.Timestamp(end_time))
        ]
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


def render_filters(df: pd.DataFrame, config: AgentConfig) -> tuple[str, str, str, tuple | None, str]:
    with st.container(border=True):
        st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)
        cols = st.columns(4, gap="medium")

        with cols[0]:
            fab_options = [ALL_OPTION] + sorted(df["fab"].astype(str).unique().tolist())
            selected_fab = st.selectbox("FAB", fab_options, key=f"{config.key}_fab")

        point_source = df if selected_fab == ALL_OPTION else df[df["fab"].astype(str) == selected_fab]
        with cols[1]:
            point_options = [ALL_OPTION] + sorted(point_source["point"].astype(str).unique().tolist())
            selected_point = st.selectbox("Point", point_options, key=f"{config.key}_point")

        selected_type = ALL_OPTION
        selected_time_range = None
        time_values = df["_time_dt"].dropna() if "_time_dt" in df.columns else pd.Series(dtype="datetime64[ns]")
        with cols[2]:
            if not time_values.empty:
                min_time = time_values.min().to_pydatetime()
                max_time = time_values.max().to_pydatetime()
                if min_time == max_time:
                    max_time = min_time + timedelta(minutes=1)
                selected_time_range = st.slider(
                    "Time range",
                    min_value=min_time,
                    max_value=max_time,
                    value=(min_time, max_time),
                    step=timedelta(minutes=30),
                    format="YYYY-MM-DD HH:mm:ss",
                    key=f"{config.key}_time_range",
                )

        with cols[3]:
            keyword = st.text_input(
                "Search",
                placeholder="time, type, judgement, log, video path",
                key=f"{config.key}_keyword",
            )

    return selected_fab, selected_point, selected_type, selected_time_range, keyword


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
        caption = f"{selected_image_label} · {selected_path.name}"
        if selected_image_label == "Diff Visualization":
            render_zoomable_diff_image(
                selected_path,
                caption,
                component_key=f"{config.key}_case_{int(row['case_no'])}_diff_zoom",
            )
        else:
            st.image(
                str(selected_path),
                caption=caption,
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


def render_video_case(row: pd.Series) -> None:
    video_path = resolve_video_path(row["video_path"])
    leak_time = float(row["leak_detection_time_sec"])

    if not video_path.exists():
        st.error(f"Video file was not found: {video_path}")
        return

    data_uri, error = video_data_uri(str(row["video_path"]))
    if error or not data_uri:
        st.error(error or "Could not load video.")
        return

    component_id = f"wl_case_{int(row['case_no'])}"
    components.html(
        f"""
        <div class="wl-viewer">
            <style>
                .wl-viewer {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: #13202e;
                    padding-bottom: 4px;
                }}
                .wl-grid {{
                    display: grid;
                    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
                    gap: 16px;
                    align-items: start;
                }}
                .wl-panel {{
                    min-width: 0;
                }}
                .wl-label {{
                    font-size: 14px;
                    font-weight: 800;
                    margin: 0 0 8px;
                }}
                .wl-video,
                .wl-canvas {{
                    display: block;
                    border: 1px solid #d9e1eb;
                    border-radius: 8px;
                    background: #0b1220;
                    box-sizing: border-box;
                }}
                .wl-video {{
                    width: 100%;
                    max-height: 460px;
                    object-fit: contain;
                }}
                .wl-canvas {{
                    width: 100%;
                    max-width: 100%;
                    max-height: 460px;
                    height: auto;
                }}
                @media (max-width: 900px) {{
                    .wl-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
            <div class="wl-grid">
                <div class="wl-panel">
                    <p class="wl-label">Patrol Video</p>
                    <video id="{component_id}_video" class="wl-video" controls preload="metadata" src={json.dumps(data_uri)}></video>
                </div>
                <div class="wl-panel">
                    <p class="wl-label">Detected Frame at {leak_time:g} sec</p>
                    <canvas id="{component_id}_canvas" class="wl-canvas"></canvas>
                </div>
            </div>
            <script>
                const video = document.getElementById("{component_id}_video");
                const canvas = document.getElementById("{component_id}_canvas");
                const targetTime = {json.dumps(leak_time)};
                let captured = false;

                function captureFrame() {{
                    if (captured || !video.videoWidth || !video.videoHeight) return;
                    captured = true;
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                }}

                video.addEventListener("loadedmetadata", () => {{
                    const safeTime = Math.min(Math.max(targetTime, 0), Math.max(video.duration - 0.05, 0));
                    video.currentTime = safeTime;
                }});

                video.addEventListener("seeked", captureFrame);
            </script>
        </div>
        """,
        height=600,
    )


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

        if config.media_mode == "video":
            render_video_case(row)
            return

        media_col, detail_col = st.columns([1.45, 1], gap="large")
        with media_col:
            if config.media_mode == "comparison":
                render_comparison_images(row, config)

        with detail_col:
            if config.media_mode == "comparison":
                render_result_box("Abnormal Type", row["abnormal_type"], danger=True)
                st.write("")
                render_result_box("Report", row["abnormal_report"])
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

    render_header(config, total_count=len(df), filtered_count=len(df))

    selected_fab, selected_point, selected_type, selected_time_range, keyword = render_filters(df, config)
    filtered = filter_results(df, selected_fab, selected_point, selected_type, selected_time_range, keyword)

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
            "Switch between visual change and water leak agents from one dashboard."
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
