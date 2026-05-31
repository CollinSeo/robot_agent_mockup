from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
CSV_PATH = ROOT / "output_table.csv"

REQUIRED_COLUMNS = [
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
]

DISPLAY_COLUMNS = [
    "case_no",
    "fab",
    "point",
    "time",
    "abnormal_type",
    "abnormal_report",
    "analysis_log",
    "action_guide",
]


st.set_page_config(
    page_title="이상 변경 자동 판단 Agent",
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

        .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 14px 34px rgba(18, 32, 46, 0.08);
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

        .result-box {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
            background: #fbfdff;
            min-height: 128px;
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

        .image-shell {
            background: #0b1220;
            border: 1px solid #111827;
            border-radius: 8px;
            padding: 10px;
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


def load_results() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, encoding="utf-8")
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"CSV 필수 컬럼 누락: {', '.join(missing_columns)}")

    df = df.copy()
    df["case_no"] = range(1, len(df) + 1)
    df["case_id"] = (
        df["fab"].astype(str)
        + " / "
        + df["point"].astype(str)
        + " / "
        + df["time"].astype(str)
    )
    return df


def resolve_image_path(raw_path: str) -> Path:
    path_text = str(raw_path).strip().replace("\\", "/")
    if path_text.startswith("./"):
        path_text = path_text[2:]

    candidate = ROOT / path_text
    if candidate.suffix:
        return candidate

    for suffix in (".png", ".jpeg", ".jpg", ".webp"):
        with_suffix = candidate.with_suffix(suffix)
        if with_suffix.exists():
            return with_suffix

    return candidate.with_suffix(".png")


def render_sidebar_metric(label: str, value: int) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <strong>{value}</strong>
            <span>{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_box(label: str, text: str, action: bool = False) -> None:
    action_class = " action" if action else ""
    st.markdown(
        f"""
        <div class="result-box{action_class}">
            <div class="result-label">{label}</div>
            <div class="result-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(total_count: int, filtered_count: int) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Agent 1</div>
            <div class="title-row">
                <div>
                    <div class="title">이상 변경 자동 판단 결과</div>
                    <div class="subtitle">
                        먼저 결과 테이블에서 케이스를 선택하면, 아래에 해당 시점의 기준 이미지,
                        현재 이미지, Diff 시각화와 CSV 기반 상세 판단 내용이 표시됩니다.
                    </div>
                </div>
                <div class="status-badge">표시 {filtered_count} / 전체 {total_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chips(row: pd.Series) -> None:
    st.markdown(
        f"""
        <span class="chip">Case {int(row["case_no"]):02d}</span>
        <span class="chip">{row["fab"]}</span>
        <span class="chip">{row["point"]}</span>
        <span class="chip">{row["time"]}</span>
        <span class="chip danger">{row["abnormal_type"]}</span>
        """,
        unsafe_allow_html=True,
    )


def filter_results(df: pd.DataFrame, selected_fab: str, selected_point: str, keyword: str) -> pd.DataFrame:
    filtered = df.copy()
    if selected_fab != "전체":
        filtered = filtered[filtered["fab"].astype(str) == selected_fab]
    if selected_point != "전체":
        filtered = filtered[filtered["point"].astype(str) == selected_point]
    if keyword.strip():
        keyword_lower = keyword.strip().lower()
        search_columns = [
            "fab",
            "point",
            "time",
            "abnormal_type",
            "abnormal_report",
            "analysis_log",
            "action_guide",
        ]
        search_text = filtered[search_columns].astype(str).agg(" ".join, axis=1).str.lower()
        filtered = filtered[search_text.str.contains(keyword_lower, regex=False)]
    return filtered


def render_case_table(filtered: pd.DataFrame) -> pd.Series:
    filtered = filtered.reset_index(drop=True)
    visible_case_numbers = set(filtered["case_no"].astype(int).tolist())
    if (
        "selected_case_no" not in st.session_state
        or int(st.session_state.selected_case_no) not in visible_case_numbers
    ):
        st.session_state.selected_case_no = int(filtered.iloc[0]["case_no"])

    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title">
                <div>
                    <h3>이상 감지 케이스 목록</h3>
                    <p>표의 행을 선택하면 해당 케이스의 이미지와 상세 텍스트가 아래에 표시됩니다.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        table_df = filtered[DISPLAY_COLUMNS].reset_index(drop=True)
        selected_index = int(
            filtered.index[filtered["case_no"].astype(int) == int(st.session_state.selected_case_no)][0]
        )
        table_key = "case_table_" + "_".join(filtered["case_no"].astype(str).tolist())
        table_event = st.dataframe(
            table_df,
            width="stretch",
            hide_index=True,
            height=225,
            on_select="rerun",
            selection_mode="single-row-required",
            selection_default={"selection": {"rows": [selected_index]}},
            row_height=30,
            key=table_key,
            column_config={
                "case_no": st.column_config.NumberColumn("Case", width="small"),
                "fab": st.column_config.TextColumn("FAB", width="small"),
                "point": st.column_config.TextColumn("지점", width="medium"),
                "time": st.column_config.TextColumn("시점", width="small"),
                "abnormal_type": st.column_config.TextColumn("이상 유형", width="medium"),
                "abnormal_report": st.column_config.TextColumn("판단 근거", width="large"),
                "analysis_log": st.column_config.TextColumn("분석 로그", width="large"),
                "action_guide": st.column_config.TextColumn("조치 사항", width="large"),
            },
        )

        selected_rows = table_event.selection.rows
        if selected_rows:
            selected_index = selected_rows[0]
            st.session_state.selected_case_no = int(filtered.iloc[selected_index]["case_no"])

        selected_row = filtered[
            filtered["case_no"].astype(int) == int(st.session_state.selected_case_no)
        ].iloc[0]
        st.markdown(
            f"""
            <div class="case-row-current">
                선택됨: Case {int(selected_row["case_no"]):02d} ·
                {selected_row["fab"]} · {selected_row["point"]} ·
                {selected_row["time"]} · {selected_row["abnormal_type"]}
            </div>
            """,
            unsafe_allow_html=True,
        )
    return selected_row


def render_selected_case(row: pd.Series) -> None:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="panel-title">
                <div>
                    <h3>선택 케이스 상세</h3>
                    <p>{row["case_id"]}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_chips(row)

        image_paths = {
            "기준 이미지": resolve_image_path(row["reference_image_path"]),
            "현재 이미지": resolve_image_path(row["current_image_path"]),
            "Diff 시각화": resolve_image_path(row["diff_visualization_path"]),
        }

        image_col, detail_col = st.columns([1.45, 1], gap="large")

        with image_col:
            selected_image_label = st.radio(
                "대표 이미지 선택",
                list(image_paths.keys()),
                index=2,
                horizontal=True,
            )
            selected_path = image_paths[selected_image_label]
            if selected_path.exists():
                st.image(
                    str(selected_path),
                    caption=f"{selected_image_label} · {selected_path.name}",
                    use_container_width=True,
                )
            else:
                st.error(f"{selected_image_label} 파일을 찾을 수 없습니다: {selected_path}")

            thumb_cols = st.columns(3)
            for col, (label, path) in zip(thumb_cols, image_paths.items()):
                with col:
                    if path.exists():
                        st.image(str(path), caption=label, use_container_width=True)
                    else:
                        st.warning(f"{label} 없음")

        with detail_col:
            render_result_box("이상 유형", str(row["abnormal_type"]))
            st.write("")
            render_result_box("판단 근거", str(row["abnormal_report"]))
            st.write("")
            render_result_box("분석 로그", str(row["analysis_log"]))
            st.write("")
            render_result_box("조치 사항", str(row["action_guide"]), action=True)


def main() -> None:
    inject_style()

    try:
        df = load_results()
    except Exception as exc:
        st.error(f"결과 CSV를 읽을 수 없습니다: {exc}")
        st.stop()

    with st.sidebar:
        st.markdown("## 이상 변경 자동 판단")
        st.caption("output_table.csv와 test_images 폴더를 기반으로 결과를 표시합니다.")

        metric_cols = st.columns(2)
        with metric_cols[0]:
            render_sidebar_metric("전체 케이스", len(df))
        with metric_cols[1]:
            render_sidebar_metric("감시 지점", df[["fab", "point"]].drop_duplicates().shape[0])

        fab_options = ["전체"] + sorted(df["fab"].astype(str).unique().tolist())
        selected_fab = st.selectbox("FAB", fab_options)

        point_source = df if selected_fab == "전체" else df[df["fab"].astype(str) == selected_fab]
        point_options = ["전체"] + sorted(point_source["point"].astype(str).unique().tolist())
        selected_point = st.selectbox("지점", point_options)

        keyword = st.text_input("검색", placeholder="time, 이상 유형, 판단 근거, 조치 사항")

    filtered = filter_results(df, selected_fab, selected_point, keyword)

    render_header(total_count=len(df), filtered_count=len(filtered))

    if filtered.empty:
        st.warning("필터 조건에 맞는 케이스가 없습니다.")
        return

    top_cols = st.columns(4)
    top_cols[0].metric("표시 중", len(filtered))
    top_cols[1].metric("전체 케이스", len(df))
    top_cols[2].metric("감시 지점", df[["fab", "point"]].drop_duplicates().shape[0])
    top_cols[3].metric("이상 판단", len(df))

    selected_row = render_case_table(filtered)
    st.write("")
    render_selected_case(selected_row)


if __name__ == "__main__":
    main()
