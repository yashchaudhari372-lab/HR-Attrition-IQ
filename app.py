import os
import io
import pickle
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

try:
    import snowflake.connector
except ImportError:
    snowflake = None

load_dotenv()
st.set_page_config(page_title="HR Attrition Intelligence", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# ---------- Design system ----------
THEMES = {
    "Midnight Multicolour": {"bg":"#0B1120","panel":"#111A2E","sidebar":"#080D19","text":"#F1F5F9","muted":"#9AAAC0","border":"#26334A","blue":"#2563EB","purple":"#8B5CF6","cyan":"#06B6D4","green":"#10B981","amber":"#F59E0B","red":"#EF4444","plot":"#111A2E"},
    "Light Professional": {"bg":"#F8FAFC","panel":"#FFFFFF","sidebar":"#FFFFFF","text":"#172033","muted":"#64748B","border":"#E2E8F0","blue":"#2563EB","purple":"#8B5CF6","cyan":"#0891B2","green":"#059669","amber":"#D97706","red":"#DC2626","plot":"#FFFFFF"},
    "Aurora Gradient": {"bg":"#0B1120","panel":"#111A2E","sidebar":"#080D19","text":"#F1F5F9","muted":"#A5B4D0","border":"#2C3654","blue":"#3B82F6","purple":"#A855F7","cyan":"#22D3EE","green":"#34D399","amber":"#FBBF24","red":"#FB7185","plot":"#111A2E"},
    "Emerald Executive": {"bg":"#071B1A","panel":"#0E2927","sidebar":"#051311","text":"#ECFDF5","muted":"#9BBDB3","border":"#234640","blue":"#0EA5E9","purple":"#14B8A6","cyan":"#2DD4BF","green":"#10B981","amber":"#F59E0B","red":"#F87171","plot":"#0E2927"},
    "Sunset Analytics": {"bg":"#1A1024","panel":"#281632","sidebar":"#130B1C","text":"#FFF7FB","muted":"#D0B7D0","border":"#4A2A4B","blue":"#8B5CF6","purple":"#C084FC","cyan":"#FB7185","green":"#34D399","amber":"#F97316","red":"#EF4444","plot":"#281632"},
}
ATTRITION_COLORS = {"No": "#3B82F6", "Yes": "#EF4444"}
MODEL_PATHS = [Path("models/attrition_model.pkl"), Path("attrition_model.pkl")]

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight Multicolour"
if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview Dashboard"

T = THEMES.get(st.session_state.theme_name, THEMES["Midnight Multicolour"])
st.markdown(f"""
<style>
:root {{ color-scheme: {'light' if st.session_state.theme_name == 'Light Professional' else 'dark'}; }}
.stApp {{ background: {T['bg']}; color: {T['text']}; }}
[data-testid="stSidebar"] {{ background: {T['sidebar']}; border-right: 1px solid {T['border']}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMarkdownContainer"] p, label, h1, h2, h3, h4 {{ color: {T['text']}; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1600px; }}
div[data-testid="stMetric"] {{ background: {T['panel']}; border: 1px solid {T['border']}; border-radius: 16px; padding: 18px 20px; box-shadow: 0 8px 24px rgba(0,0,0,.10); transition: transform .18s ease, border-color .18s ease; }}
div[data-testid="stMetric"]:hover {{ transform: translateY(-2px); border-color: {T['cyan']}; }}
div[data-testid="stMetricValue"] {{ font-size: clamp(1.4rem, 2.3vw, 2.1rem); font-weight: 750; color: {T['text']}; }}
div[data-testid="stMetricLabel"] {{ color: {T['muted']}; }}
.stButton > button, .stDownloadButton > button {{ border-radius: 10px; border: 1px solid {T['border']}; font-weight: 650; transition: all .18s ease; }}
.stButton > button[kind="primary"] {{ background: linear-gradient(110deg, {T['blue']}, {T['purple']}); color: white; border: 0; }}
.stButton > button:hover, .stDownloadButton > button:hover {{ border-color: {T['cyan']}; transform: translateY(-1px); }}
section[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stHorizontalBlock"]) {{ gap: 1rem; }}
.hai-brand {{ padding: 16px 4px 20px; border-bottom: 1px solid {T['border']}; margin-bottom: 16px; }}
.hai-mark {{ display:inline-flex; width:42px; height:42px; border-radius:13px; align-items:center; justify-content:center; background:linear-gradient(135deg,{T['blue']},{T['purple']},{T['cyan']}); font-size:22px; margin-right:10px; vertical-align:middle; }}
.hai-title {{ font-size:1.35rem; font-weight:800; letter-spacing:-.03em; }}
.hai-subtitle {{ color:{T['muted']}; font-size:.78rem; line-height:1.55; margin-top:10px; }}
.hai-hero {{ background:linear-gradient(115deg,{T['panel']}, {T['bg']}); border:1px solid {T['border']}; border-radius:20px; padding:24px 26px; margin:6px 0 22px; }}
.hai-eyebrow {{ color:{T['cyan']}; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:800; }}
.hai-hero h1 {{ margin:.35rem 0 .45rem; font-size:clamp(1.65rem,3vw,2.45rem); letter-spacing:-.04em; }}
.hai-hero p {{ color:{T['muted']}; margin:0; }}
.hai-card {{ background:{T['panel']}; border:1px solid {T['border']}; border-radius:16px; padding:18px 20px; height:100%; }}
.hai-muted {{ color:{T['muted']}; font-size:.9rem; }}
hr {{ border-color:{T['border']}; }}
@media(max-width:700px) {{ .block-container {{ padding:1rem .75rem; }} .hai-hero {{ padding:18px; }} }}
</style>
""", unsafe_allow_html=True)


def find_model():
    for path in MODEL_PATHS:
        if path.exists():
            with path.open("rb") as f:
                return pickle.load(f), path
    return None, None


@st.cache_resource(show_spinner=False)
def load_model(path_string):
    with open(path_string, "rb") as f:
        return pickle.load(f)


@st.cache_data(ttl=600, show_spinner=False)
def load_data():
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Snowflake configuration is incomplete. Set the required environment variables in .env or Streamlit secrets.")
    if snowflake is None:
        raise RuntimeError("snowflake-connector-python is not installed. Install requirements.txt and retry.")
    conn = None
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"), password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"), warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"), schema=os.getenv("SNOWFLAKE_SCHEMA"),
            login_timeout=20, network_timeout=30,
        )
        return pd.read_sql_query("SELECT * FROM hr_attrition_final", conn)
    finally:
        if conn is not None:
            conn.close()


def safe_num(series, default=0):
    return pd.to_numeric(series, errors="coerce").fillna(default)


def rate_yes(frame):
    if frame.empty or "ATTRITION" not in frame:
        return 0.0
    return float((frame["ATTRITION"].astype(str).str.title() == "Yes").mean() * 100)


def clean_df(frame):
    data = frame.copy()
    data.columns = [str(c).upper() for c in data.columns]
    if "ATTRITION" in data:
        data["ATTRITION"] = data["ATTRITION"].astype(str).str.title()
    return data


def chart_layout(fig, title=None, height=360):
    fig.update_layout(
        title=title, height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=T["plot"],
        font=dict(color=T["text"], family="Inter, Segoe UI, sans-serif"),
        margin=dict(l=12, r=12, t=55 if title else 20, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor=T["panel"], font_color=T["text"]),
    )
    fig.update_xaxes(gridcolor=T["border"], zerolinecolor=T["border"])
    fig.update_yaxes(gridcolor=T["border"], zerolinecolor=T["border"])
    return fig


def show_chart(fig, key=None):
    st.plotly_chart(fig, use_container_width=True, theme=None, key=key, config={"displaylogo": False, "responsive": True, "toImageButtonOptions": {"format": "png", "scale": 2}})


def render_empty():
    st.info("No employees match the current filters. Reset or broaden the filters to see analytics.")


def _reset_filter_state():
    for key in ["flt_dept", "flt_role", "flt_gender", "flt_age", "flt_ot", "flt_marital", "flt_income", "flt_tenure", "flt_sat"]:
        st.session_state.pop(key, None)

def filter_data(df):
    st.subheader("Filter workforce")
    with st.expander("Advanced filters", expanded=True):
        available_cols = st.columns(3)
        result = df.copy()
        if "DEPARTMENT" in df:
            opts = sorted(df["DEPARTMENT"].dropna().astype(str).unique())
            selected = available_cols[0].multiselect("Department", opts, default=opts, key="flt_dept")
            result = result[result["DEPARTMENT"].astype(str).isin(selected)]
        if "JOB_ROLE" in df:
            opts = sorted(df["JOB_ROLE"].dropna().astype(str).unique())
            selected = available_cols[1].multiselect("Job role", opts, default=opts, key="flt_role")
            result = result[result["JOB_ROLE"].astype(str).isin(selected)]
        if "GENDER" in df:
            opts = sorted(df["GENDER"].dropna().astype(str).unique())
            selected = available_cols[2].multiselect("Gender", opts, default=opts, key="flt_gender")
            result = result[result["GENDER"].astype(str).isin(selected)]
        c4, c5, c6 = st.columns(3)
        if "AGE" in df and df["AGE"].notna().any():
            lo, hi = int(safe_num(df["AGE"]).min()), int(safe_num(df["AGE"]).max())
            age_range = c4.slider("Age range", lo, hi, (lo, hi), key="flt_age")
            result = result[safe_num(result["AGE"]).between(*age_range)]
        if "OVERTIME" in df:
            opts = sorted(df["OVERTIME"].dropna().astype(str).unique())
            selected = c5.multiselect("Overtime", opts, default=opts, key="flt_ot")
            result = result[result["OVERTIME"].astype(str).isin(selected)]
        if "MARITAL_STATUS" in df:
            opts = sorted(df["MARITAL_STATUS"].dropna().astype(str).unique())
            selected = c6.multiselect("Marital status", opts, default=opts, key="flt_marital")
            result = result[result["MARITAL_STATUS"].astype(str).isin(selected)]
        c7, c8, c9 = st.columns(3)
        if "MONTHLY_INCOME" in df and df["MONTHLY_INCOME"].notna().any():
            lo, hi = int(safe_num(df["MONTHLY_INCOME"]).min()), int(safe_num(df["MONTHLY_INCOME"]).max())
            income_range = c7.slider("Monthly income", lo, hi, (lo, hi), key="flt_income")
            result = result[safe_num(result["MONTHLY_INCOME"]).between(*income_range)]
        if "YEARS_AT_COMPANY" in df and df["YEARS_AT_COMPANY"].notna().any():
            lo, hi = int(safe_num(df["YEARS_AT_COMPANY"]).min()), int(safe_num(df["YEARS_AT_COMPANY"]).max())
            tenure = c8.slider("Years at company", lo, hi, (lo, hi), key="flt_tenure")
            result = result[safe_num(result["YEARS_AT_COMPANY"]).between(*tenure)]
        if "JOB_SATISFACTION" in df:
            opts = sorted(safe_num(df["JOB_SATISFACTION"]).unique().tolist())
            selected = c9.multiselect("Job satisfaction", opts, default=opts, key="flt_sat")
            result = result[safe_num(result["JOB_SATISFACTION"]).isin(selected)]
        b1, b2 = st.columns([1, 5])
        with b1:
            st.button("Reset all filters", use_container_width=True, on_click=_reset_filter_state)
        b2.caption(f"Active result: {len(result):,} of {len(df):,} employees")
    return result


def insights_for(df):
    notes = []
    if df.empty:
        return ["No matching records are available to generate insights."]
    if {"DEPARTMENT", "ATTRITION"}.issubset(df.columns):
        rates = df.assign(_left=(df["ATTRITION"] == "Yes").astype(int)).groupby("DEPARTMENT")["_left"].mean().mul(100).dropna()
        if len(rates):
            dept = rates.idxmax()
            notes.append(f"{dept} has the highest observed department attrition rate in the current selection ({rates.max():.1f}%). This is an association, not evidence of cause.")
    if {"OVERTIME", "ATTRITION"}.issubset(df.columns):
        rates = df.assign(_left=(df["ATTRITION"] == "Yes").astype(int)).groupby("OVERTIME")["_left"].mean().mul(100).dropna()
        if len(rates) >= 2:
            notes.append("Observed attrition by overtime: " + "; ".join(f"{k}: {v:.1f}%" for k, v in rates.items()) + ". Review workload and scheduling context before drawing conclusions.")
    if {"JOB_SATISFACTION", "ATTRITION"}.issubset(df.columns):
        rates = df.assign(_left=(df["ATTRITION"] == "Yes").astype(int)).groupby("JOB_SATISFACTION")["_left"].mean().mul(100).dropna()
        if len(rates) >= 2:
            notes.append(f"The lowest-satisfaction group has {rates.iloc[0]:.1f}% observed attrition and the highest-satisfaction group has {rates.iloc[-1]:.1f}%. Check group sizes and other factors before interpreting this pattern.")
    if {"MONTHLY_INCOME", "ATTRITION"}.issubset(df.columns):
        med = df.groupby("ATTRITION")["MONTHLY_INCOME"].median()
        if "Yes" in med and "No" in med:
            notes.append(f"Median monthly income is ₹{med['Yes']:,.0f} among employees marked as left and ₹{med['No']:,.0f} among employees retained. This descriptive difference does not establish causation.")
    if {"YEARS_AT_COMPANY", "ATTRITION"}.issubset(df.columns):
        med = df.groupby("ATTRITION")["YEARS_AT_COMPANY"].median()
        if "Yes" in med and "No" in med:
            notes.append(f"Median tenure is {med['Yes']:.1f} years for employees marked as left versus {med['No']:.1f} years for retained employees.")
    return notes or ["The available columns do not support enough comparisons to generate insights."]


def pdf_report(df, theme_name):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab. Install the updated requirements.txt.") from exc
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm, topMargin=1.7*cm, bottomMargin=1.7*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Subtle", parent=styles["Normal"], textColor=colors.HexColor("#64748B"), leading=15))
    total = len(df); left = int((df.get("ATTRITION", pd.Series(dtype=str)) == "Yes").sum())
    active = total-left; attr_rate = left/total*100 if total else 0
    story = [Paragraph("HR Attrition Intelligence", styles["Title"]), Paragraph("Executive workforce analytics summary", styles["Heading2"]),
             Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · Theme: {theme_name} · Based on the active dashboard filters", styles["Subtle"]), Spacer(1, 14)]
    rows = [["Metric", "Value"], ["Employees in selection", f"{total:,}"], ["Active employees", f"{active:,}"], ["Employees who left", f"{left:,}"], ["Observed attrition rate", f"{attr_rate:.1f}%"]]
    if "MONTHLY_INCOME" in df and total: rows.append(["Average monthly income", f"₹{safe_num(df['MONTHLY_INCOME']).mean():,.0f}"])
    if "AGE" in df and total: rows.append(["Average age", f"{safe_num(df['AGE']).mean():.1f} years"])
    table = Table(rows, colWidths=[8*cm, 7*cm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2563EB")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#CBD5E1")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F5F9")]), ("PADDING", (0,0), (-1,-1), 8)]))
    story += [table, Spacer(1, 18), Paragraph("Observed insights", styles["Heading2"])]
    for item in insights_for(df): story += [Paragraph("• " + item, styles["Normal"]), Spacer(1, 7)]
    story += [Spacer(1, 8), Paragraph("Interpretation note", styles["Heading2"]), Paragraph("These statistics describe the filtered dataset and do not establish causal relationships. Model predictions should support, not replace, fair human review. This report excludes employee-level rows.", styles["Subtle"])]
    doc.build(story)
    return buffer.getvalue()

# ---------- Sidebar / data connection ----------
with st.sidebar:
    st.markdown('<div class="hai-brand"><span class="hai-mark">✦</span><span class="hai-title">HR Attrition<br>Intelligence</span><div class="hai-subtitle">Workforce Analytics<br>Employee Retention Insights<br>AI-Powered Attrition Prediction</div></div>', unsafe_allow_html=True)
    pages = ["Overview Dashboard", "Workforce Analytics", "Attrition Analysis", "AI Attrition Predictor", "Model Performance", "Employee Insights", "Reports & Downloads", "Settings"]
    page = st.radio("NAVIGATION", pages, index=pages.index(st.session_state.active_page), label_visibility="collapsed", key="nav_radio")
    st.session_state.active_page = page
    st.divider()
    st.caption("APPEARANCE")
    st.selectbox("Dashboard theme", list(THEMES), key="theme_name")
    if st.button("↻ Refresh data", use_container_width=True):
        load_data.clear()
        st.rerun()
    st.caption("Snowflake · Streamlit · Plotly · Random Forest")

# Theme change takes effect on rerun; update the selected theme immediately for this run.
T = THEMES[st.session_state.theme_name]

st.markdown(f'<div class="hai-hero"><div class="hai-eyebrow">WORKFORCE INTELLIGENCE PLATFORM</div><h1>{page}</h1><p>Workforce Analytics&nbsp; | &nbsp;Employee Retention Insights&nbsp; | &nbsp;AI-Powered Attrition Prediction</p></div>', unsafe_allow_html=True)

with st.spinner("Loading the latest workforce data from Snowflake…"):
    try:
        raw_df = load_data()
        df = clean_df(raw_df)
    except Exception as exc:
        st.error("Unable to load workforce data from Snowflake.")
        st.caption("Check your .env / Streamlit secrets, network access, database permissions, and the hr_attrition_final table. Credentials are not displayed here.")
        with st.expander("Technical details"):
            st.code(f"{type(exc).__name__}: {str(exc)[:500]}")
        st.stop()

if df.empty:
    st.warning("The Snowflake table returned no records. The dashboard needs data to calculate metrics and charts.")
    st.stop()
if "ATTRITION" not in df:
    st.error("The source table is missing the required ATTRITION column.")
    st.stop()

model_saved, model_path = find_model()
if model_saved is None:
    st.warning("Saved model not found. Place attrition_model.pkl in the project root or models/ folder to enable prediction and feature importance.")
    model = encoders = columns = None
else:
    model = model_saved.get("model"); encoders = model_saved.get("encoders", {}); columns = model_saved.get("columns", [])

# ---------- Dashboard filters ----------
filtered = df.copy()
if page in ["Overview Dashboard", "Workforce Analytics", "Attrition Analysis", "Employee Insights", "Reports & Downloads"]:
    filtered = filter_data(df)
    st.divider()

# ---------- Overview ----------
if page == "Overview Dashboard":
    total = len(filtered); left = int((filtered["ATTRITION"] == "Yes").sum()); active = total-left
    rate = left/total*100 if total else 0
    c = st.columns(4)
    c[0].metric("Total employees", f"{total:,}", help="Employees in the current filter selection")
    c[1].metric("Active employees", f"{active:,}", help="Records where ATTRITION is No")
    c[2].metric("Employees who left", f"{left:,}")
    c[3].metric("Observed attrition rate", f"{rate:.1f}%")
    c = st.columns(4)
    c[0].metric("Retention rate", f"{100-rate:.1f}%")
    c[1].metric("Avg. monthly income", f"₹{safe_num(filtered['MONTHLY_INCOME']).mean():,.0f}" if "MONTHLY_INCOME" in filtered and total else "—")
    c[2].metric("Average age", f"{safe_num(filtered['AGE']).mean():.1f}" if "AGE" in filtered and total else "—")
    c[3].metric("Avg. tenure", f"{safe_num(filtered['YEARS_AT_COMPANY']).mean():.1f} yrs" if "YEARS_AT_COMPANY" in filtered and total else "—")
    if filtered.empty:
        render_empty()
    else:
        left_col, right_col = st.columns([1.5, 1])
        with left_col:
            if "DEPARTMENT" in filtered:
                counts = filtered.groupby(["DEPARTMENT", "ATTRITION"]).size().reset_index(name="Employees")
                fig = px.bar(counts, x="DEPARTMENT", y="Employees", color="ATTRITION", barmode="group", text_auto=True, color_discrete_map=ATTRITION_COLORS, title="Attrition by department")
                show_chart(chart_layout(fig, height=390), "overview_department")
        with right_col:
            split = filtered["ATTRITION"].value_counts().rename_axis("ATTRITION").reset_index(name="Employees")
            fig = px.pie(split, names="ATTRITION", values="Employees", hole=.65, color="ATTRITION", color_discrete_map=ATTRITION_COLORS, title="Workforce retention mix")
            fig.update_traces(textinfo="percent+label", hole=.65)
            show_chart(chart_layout(fig, height=390), "overview_donut")
        c1, c2 = st.columns(2)
        with c1:
            if "OVERTIME" in filtered:
                d = filtered.groupby(["OVERTIME", "ATTRITION"]).size().reset_index(name="Employees")
                show_chart(chart_layout(px.bar(d, x="OVERTIME", y="Employees", color="ATTRITION", barmode="group", text_auto=True, color_discrete_map=ATTRITION_COLORS, title="Attrition by overtime")), "overview_overtime")
        with c2:
            if "MONTHLY_INCOME" in filtered:
                show_chart(chart_layout(px.box(filtered, x="ATTRITION", y="MONTHLY_INCOME", color="ATTRITION", points="outliers", color_discrete_map=ATTRITION_COLORS, title="Monthly income by attrition")), "overview_income")

# ---------- Workforce analytics ----------
elif page == "Workforce Analytics":
    st.subheader("Workforce composition and trends")
    if filtered.empty: render_empty()
    else:
        a, b = st.columns(2)
        with a:
            if "AGE" in filtered:
                show_chart(chart_layout(px.histogram(filtered, x="AGE", color="ATTRITION", nbins=20, marginal="box", barmode="overlay", opacity=.78, color_discrete_map=ATTRITION_COLORS, title="Age distribution")), "workforce_age")
        with b:
            if "YEARS_AT_COMPANY" in filtered:
                show_chart(chart_layout(px.histogram(filtered, x="YEARS_AT_COMPANY", color="ATTRITION", nbins=20, barmode="group", color_discrete_map=ATTRITION_COLORS, title="Tenure distribution")), "workforce_tenure")
        a, b = st.columns(2)
        with a:
            if "JOB_ROLE" in filtered:
                d = filtered.groupby(["JOB_ROLE", "ATTRITION"]).size().reset_index(name="Employees")
                show_chart(chart_layout(px.bar(d, y="JOB_ROLE", x="Employees", color="ATTRITION", barmode="group", orientation="h", color_discrete_map=ATTRITION_COLORS, title="Workforce by job role"), height=460), "workforce_roles")
        with b:
            if "GENDER" in filtered:
                d = filtered.groupby(["GENDER", "ATTRITION"]).size().reset_index(name="Employees")
                show_chart(chart_layout(px.bar(d, x="GENDER", y="Employees", color="ATTRITION", barmode="group", text_auto=True, color_discrete_map=ATTRITION_COLORS, title="Workforce by gender")), "workforce_gender")

# ---------- Attrition analysis ----------
elif page == "Attrition Analysis":
    st.subheader("Explore observed attrition patterns")
    if filtered.empty: render_empty()
    else:
        if "DEPARTMENT" in filtered:
            d = filtered.assign(_left=(filtered["ATTRITION"] == "Yes").astype(int)).groupby("DEPARTMENT").agg(Employees=("ATTRITION", "size"), Left=("_left", "sum")).reset_index()
            d["Attrition rate"] = np.where(d["Employees"] > 0, d["Left"] / d["Employees"] * 100, 0)
            a, b = st.columns(2)
            with a: show_chart(chart_layout(px.bar(d, x="DEPARTMENT", y="Attrition rate", text=d["Attrition rate"].map(lambda x: f"{x:.1f}%"), color="Attrition rate", color_continuous_scale=[T["cyan"], T["purple"], T["red"]], title="Attrition rate by department")), "attrition_dept_rate")
            with b:
                if "JOB_SATISFACTION" in filtered:
                    d2 = filtered.groupby(["JOB_SATISFACTION", "ATTRITION"]).size().reset_index(name="Employees")
                    show_chart(chart_layout(px.bar(d2, x="JOB_SATISFACTION", y="Employees", color="ATTRITION", barmode="group", text_auto=True, color_discrete_map=ATTRITION_COLORS, title="Job satisfaction vs attrition")), "attrition_satisfaction")
        a, b = st.columns(2)
        with a:
            if "DISTANCE_FROM_HOME" in filtered:
                show_chart(chart_layout(px.box(filtered, x="ATTRITION", y="DISTANCE_FROM_HOME", color="ATTRITION", color_discrete_map=ATTRITION_COLORS, title="Distance from home by attrition")), "attrition_distance")
        with b:
            if "YEARS_AT_COMPANY" in filtered:
                show_chart(chart_layout(px.violin(filtered, x="ATTRITION", y="YEARS_AT_COMPANY", color="ATTRITION", box=True, points=False, color_discrete_map=ATTRITION_COLORS, title="Tenure by attrition")), "attrition_tenure")

# ---------- Prediction ----------
elif page == "AI Attrition Predictor":
    st.subheader("Predict employee attrition risk")
    st.caption("Prediction output is a model estimate, not a calibrated real-world probability or a recommendation for employment decisions.")
    if model is None or encoders is None or not columns:
        st.error("The saved model bundle is required. Add attrition_model.pkl to the project root or models/ folder.")
    else:
        with st.form("prediction_form"):
            st.markdown("#### Employee profile")
            a, b, c = st.columns(3)
            age = a.number_input("Age", min_value=18, max_value=100, value=30)
            department = b.selectbox("Department", encoders["DEPARTMENT"].classes_.tolist())
            job_role = c.selectbox("Job role", encoders["JOB_ROLE"].classes_.tolist())
            gender = a.selectbox("Gender", encoders["GENDER"].classes_.tolist())
            marital = b.selectbox("Marital status", encoders["MARITAL_STATUS"].classes_.tolist())
            performance = c.slider("Performance rating", 1, 4, 3)
            st.markdown("#### Work and engagement")
            a, b, c = st.columns(3)
            overtime = a.selectbox("Overtime", encoders["OVERTIME"].classes_.tolist())
            distance = b.number_input("Distance from home (km)", 0, 500, 10)
            income = c.number_input("Monthly income (₹)", 0, 1000000, 50000, step=1000)
            years = a.number_input("Years at company", 0, 60, 3)
            satisfaction = b.slider("Job satisfaction", 1, 4, 3)
            submitted = st.form_submit_button("✦ Predict attrition risk", type="primary", use_container_width=True)
        if submitted:
            try:
                row = {"AGE": age, "DEPARTMENT": encoders["DEPARTMENT"].transform([department])[0], "JOB_ROLE": encoders["JOB_ROLE"].transform([job_role])[0], "GENDER": encoders["GENDER"].transform([gender])[0], "MARITAL_STATUS": encoders["MARITAL_STATUS"].transform([marital])[0], "PERFORMANCE_RATING": performance, "OVERTIME": encoders["OVERTIME"].transform([overtime])[0], "DISTANCE_FROM_HOME": distance, "MONTHLY_INCOME": income, "YEARS_AT_COMPANY": years, "JOB_SATISFACTION": satisfaction}
                input_df = pd.DataFrame([row]).reindex(columns=columns)
                pred = int(model.predict(input_df)[0])
                probabilities = model.predict_proba(input_df)[0]
                classes = list(model.classes_)
                yes_idx = classes.index(1) if 1 in classes else (classes.index("Yes") if "Yes" in classes else len(probabilities)-1)
                prob = float(probabilities[yes_idx])
                band = "Low" if prob < .30 else ("Moderate" if prob < .60 else "High")
                color = {"Low": T["green"], "Moderate": T["amber"], "High": T["red"]}[band]
                x, y = st.columns([1, 1.4])
                with x:
                    st.markdown(f'<div class="hai-card"><div class="hai-eyebrow">MODEL CLASSIFICATION</div><h2 style="color:{color};margin:.6rem 0">{"Attrition predicted" if pred == 1 else "Retention predicted"}</h2><p class="hai-muted">Probability band: <b>{band}</b> (configurable display band)</p><p class="hai-muted">Band thresholds: Low &lt; 30%, Moderate 30–59.9%, High ≥ 60%.</p></div>', unsafe_allow_html=True)
                with y:
                    gauge = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={"suffix":"%"}, title={"text":"Model-estimated attrition probability"}, gauge={"axis":{"range":[0,100]},"bar":{"color":color},"bgcolor":T["panel"],"bordercolor":T["border"],"steps":[{"range":[0,30],"color":"rgba(16,185,129,.18)"},{"range":[30,60],"color":"rgba(245,158,11,.18)"},{"range":[60,100],"color":"rgba(239,68,68,.18)"}]}))
                    show_chart(chart_layout(gauge, height=290), "risk_gauge")
                st.progress(min(100, max(0, int(prob*100))))
                st.info("Probability is the model's output from the saved classifier. The low/moderate/high band is a display convention and does not imply probability calibration.")
            except Exception as exc:
                st.error("Prediction could not be generated. Verify that the saved model and encoders match the current application.")
                st.caption(f"Technical details: {type(exc).__name__}: {str(exc)[:250]}")

# ---------- Model performance ----------
elif page == "Model Performance":
    st.subheader("Model transparency and performance")
    if model is None:
        st.warning("The saved model bundle is not available, so model details cannot be shown.")
    else:
        st.markdown("#### Current model profile")
        a, b, c = st.columns(3)
        a.metric("Algorithm", "Random Forest")
        b.metric("Input features", f"{len(columns)}")
        c.metric("Trees", f"{getattr(model, 'n_estimators', '—')}")
        st.markdown("""
        <div class="hai-card">
        <b>How this model was trained</b><br><br>
        The supplied training script encodes categorical columns with LabelEncoder, maps Attrition Yes/No to 1/0, splits the data into an 80/20 stratified train/test split, applies SMOTE to the training partition, and tunes a Random Forest using 3-fold GridSearchCV with F1 scoring. The saved artifact contains the fitted estimator, encoders and ordered input columns.<br><br>
        <b>Important limitation:</b> the uploaded model bundle does not contain a saved held-out evaluation report. Current test-set accuracy, precision, recall, F1, confusion matrix and ROC-AUC therefore cannot be verified from the artifact alone. This page intentionally does not invent them. Re-evaluate on a documented untouched test set before reporting these metrics.
        </div>
        """, unsafe_allow_html=True)
        if hasattr(model, "feature_importances_") and columns:
            imp = pd.Series(model.feature_importances_, index=columns).sort_values().tail(11).reset_index()
            imp.columns = ["Feature", "Importance"]
            show_chart(chart_layout(px.bar(imp, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale=[T["cyan"], T["purple"]], title="Random Forest feature importance"), height=430), "model_importance")
            st.caption("Feature importance describes how the fitted model used features; it is not proof of causation or an explanation for an individual prediction.")
        st.markdown("#### Model limitations")
        st.markdown("- A probability score is not automatically calibrated to real-world likelihood.\n- Historical patterns may reflect data quality issues or structural bias.\n- The current training script uses label encoding for categorical predictors; this may impose artificial ordering on categories.\n- Validate performance, fairness, drift and calibration before operational use.")

# ---------- Employee insights ----------
elif page == "Employee Insights":
    st.subheader("Retention insights from the selected workforce")
    for idx, note in enumerate(insights_for(filtered), 1):
        st.markdown(f'<div class="hai-card" style="margin-bottom:10px"><span class="hai-eyebrow">INSIGHT {idx:02d}</span><p style="margin:.55rem 0 0">{note}</p></div>', unsafe_allow_html=True)
    st.markdown("#### Practical retention actions to consider")
    st.markdown("- Validate workload and overtime patterns with employee feedback and team-level context.\n- Review onboarding, career progression and manager support for groups with elevated observed attrition.\n- Examine pay bands and internal equity with appropriate privacy safeguards.\n- Track engagement and job satisfaction over time; use aggregated results where possible.\n- Treat analytics as a prompt for supportive investigation, not as the sole basis for individual employment decisions.")
    st.caption("Insights are descriptive associations from the current filtered dataset. They do not establish why employees leave.")

# ---------- Reports ----------
elif page == "Reports & Downloads":
    st.subheader("Reports and data exports")
    st.write("Downloads use the current filter selection. Employee-level exports can contain sensitive workforce data; store and share them according to your organization's access policies.")
    csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇ Download filtered data (CSV)", data=csv_bytes, file_name="hr_attrition_filtered.csv", mime="text/csv", use_container_width=True)
    x1, x2 = st.columns(2)
    with x1:
        try:
            excel = io.BytesIO()
            with pd.ExcelWriter(excel, engine="openpyxl") as writer:
                filtered.to_excel(writer, index=False, sheet_name="Filtered Employees")
                summary = pd.DataFrame({"Metric":["Employees in selection","Active employees","Employees who left","Observed attrition rate (%)"],"Value":[len(filtered), int((filtered["ATTRITION"]=="No").sum()), int((filtered["ATTRITION"]=="Yes").sum()), round(rate_yes(filtered),2)]})
                summary.to_excel(writer, index=False, sheet_name="Summary")
            st.download_button("⬇ Download filtered data (Excel)", data=excel.getvalue(), file_name="hr_attrition_filtered.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        except Exception as exc:
            st.error(f"Excel export unavailable: {exc}")
    with x2:
        try:
            pdf = pdf_report(filtered, st.session_state.theme_name)
            st.download_button("⬇ Download executive summary (PDF)", data=pdf, file_name="hr_attrition_executive_summary.pdf", mime="application/pdf", use_container_width=True)
        except Exception as exc:
            st.warning(str(exc))
    st.divider()
    st.markdown("#### Executive summary preview")
    n = len(filtered); left = int((filtered["ATTRITION"] == "Yes").sum()); rate = left/n*100 if n else 0
    st.markdown(f"The current selection contains **{n:,} employees**. **{left:,}** are marked as having left, corresponding to an observed attrition rate of **{rate:.1f}%**. This summary is based on the active filters and is descriptive rather than causal.")
    for note in insights_for(filtered): st.write("• " + note)

# ---------- Settings ----------
elif page == "Settings":
    st.subheader("Workspace settings and data status")
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="hai-card"><b>Appearance</b><p class="hai-muted">Choose one of five palettes from the sidebar. The selection persists across Streamlit reruns in the current session.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="hai-card" style="margin-top:12px"><b>Privacy and security</b><p class="hai-muted">Credentials are read from environment variables or Streamlit secrets and are not shown in the UI. Avoid committing .env, model artifacts containing sensitive information, or employee exports to public repositories.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="hai-card"><b>Data connection</b>', unsafe_allow_html=True)
        st.write("Source: Snowflake")
        st.write("Table: `hr_attrition_final`")
        st.write(f"Rows loaded: **{len(df):,}**")
        st.write(f"Columns loaded: **{len(df.columns)}**")
        st.write(f"Last page load: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
        st.write(f"Model file: **{str(model_path) if model_path else 'Not found'}**")
        if st.button("Clear cached data and reload", type="primary"):
            load_data.clear(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.markdown(f'<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:{T["muted"]};font-size:.8rem"><span>© {datetime.now().year} HR Attrition Intelligence</span><span>Built with Streamlit · Python · Snowflake · Plotly · Scikit-learn</span><span>Insights support decisions; they do not replace human judgment.</span></div>', unsafe_allow_html=True)
