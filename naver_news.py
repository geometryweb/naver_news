# ============================================================
# 네이버 실시간 뉴스 검색 대시보드 (NCP API Gateway)
# naver_news.py  — Modern Redesign (Light table fix)
# ============================================================
import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# ── .env 로드 ──────────────────────────────────────────────
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

# ── 페이지 설정 ────────────────────────────────────────────
st.set_page_config(
    page_title="네이버 뉴스 인사이트",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  THEME CSS
# ═══════════════════════════════════════════════════════════
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

/* 시스템/브라우저 라이트모드 + Streamlit system theme 무시하고 앱 내부 다크 테마 강제 */
html {
    color-scheme: dark !important;
}
:root, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp, body {
    color-scheme: dark !important;
    /* Streamlit 내장 테마 변수 강제 오버라이드 */
    --background-color: #0b0f14 !important;
    --secondary-background-color: #12181f !important;
    --primary-color: #03C75A !important;
    --text-color: #e8edf4 !important;
    --font: "Noto Sans KR", sans-serif !important;
    --secondary-text-color: #8b97a8 !important;
    --widget-background-color: #1a222d !important;
    --widget-border-color: #2a3441 !important;
}

:root {
    --bg-primary: #0b0f14;
    --bg-secondary: #12181f;
    --bg-card: #1a222d;
    --bg-elevated: #222c38;
    --text-primary: #e8edf4;
    --text-secondary: #8b97a8;
    --text-muted: #5c6b7a;
    --accent: #03C75A;
    --accent-soft: rgba(3,199,90,0.12);
    --accent-glow: rgba(3,199,90,0.25);
    --border: #2a3441;
    --border-soft: #1e2733;
    --danger: #ff6b6b;
    --warning: #ffc107;
    --info: #4dabf7;
    --radius: 14px;
    --radius-sm: 10px;
    --shadow: 0 4px 24px rgba(0,0,0,0.35);
}
* { font-family: 'Noto Sans KR', sans-serif !important; }

[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-symbols-outlined,
.material-symbols-rounded,
.material-icons {
    font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Icons", sans-serif !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
/* 사이드바 글자색은 개별 요소에만 적용 (셀렉트박스 내부 글자색 덮어쓰지 않음) */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p {
    color: var(--text-primary) !important;
}

/* 검색어 입력창 — 이중 테두리 제거, 단일 테두리만 */
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div,
[data-testid="stDateInput"] > div > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input,
.stDateInput > div > div > input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
    outline: none !important;
}
.stButton > button {
    background: linear-gradient(135deg, #03C75A, #02a84e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px var(--accent-glow) !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #03C75A, #02a84e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
}
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetric"] label { color: var(--text-secondary) !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-primary) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm);
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #fff !important;
}

div[data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
}
div[data-baseweb="select"] span { color: var(--text-primary) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

.hero {
    background: linear-gradient(135deg, rgba(3,199,90,0.08) 0%, rgba(3,199,90,0.02) 60%, transparent 100%);
    border: 1px solid rgba(3,199,90,0.2);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
}
.hero h1 {
    color: var(--accent) !important;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.02em;
}
.hero p {
    color: var(--text-secondary) !important;
    margin: 0;
    font-size: 0.92rem;
}
.sidebar-brand {
    text-align: center;
    padding: 0.8rem 0 1.2rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.sidebar-brand h2 {
    color: var(--accent) !important;
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
}
.sidebar-brand p {
    color: var(--text-muted) !important;
    font-size: 0.75rem;
    margin: 0.25rem 0 0;
}
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.15rem 1.3rem;
    margin-bottom: 0.85rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.news-card:hover {
    border-color: rgba(3,199,90,0.4);
    box-shadow: 0 4px 20px rgba(3,199,90,0.08);
}
.news-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.news-title a {
    color: var(--text-primary) !important;
    text-decoration: none;
}
.news-title a:hover { color: var(--accent) !important; }
.news-desc {
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.55;
    margin-bottom: 0.65rem;
}
.news-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem 1rem;
    align-items: center;
}
.news-meta a {
    color: var(--accent) !important;
    text-decoration: none;
    font-weight: 500;
}
.badge {
    display: inline-flex;
    align-items: center;
    background: var(--accent-soft);
    color: var(--accent);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-neutral {
    background: rgba(139,151,168,0.15);
    color: var(--text-secondary);
}
.chip {
    display: inline-block;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    margin: 2px 4px 2px 0;
    cursor: default;
}
.chip-hot {
    background: var(--accent-soft);
    border-color: rgba(3,199,90,0.3);
    color: var(--accent);
    font-weight: 600;
}
.insight-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    height: 100%;
}
.insight-box h4 {
    margin: 0 0 0.5rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.footer-note {
    font-size: 0.72rem;
    text-align: center;
    opacity: 0.5;
    margin-top: 1rem;
}
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-secondary);
}
.empty-state .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

.dark-table-wrap {
    width: 100%;
    max-height: 420px;
    overflow: auto;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--bg-card);
    box-shadow: var(--shadow);
}
.dark-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    color: var(--text-primary);
    background: var(--bg-card);
}
.dark-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: var(--bg-elevated);
    color: var(--text-primary);
    font-weight: 600;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
}
.dark-table tbody td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-soft);
    vertical-align: top;
    color: var(--text-primary);
    background: var(--bg-card);
}
.dark-table tbody tr:hover td {
    background: var(--bg-elevated);
}
.dark-table .td-idx {
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
.dark-table .td-title {
    font-weight: 500;
    max-width: 280px;
    color: var(--text-primary);
}
.dark-table .td-desc {
    color: var(--text-secondary);
    max-width: 360px;
}
.dark-table .td-domain {
    color: var(--text-secondary);
    font-size: 0.8rem;
}
.dark-table .td-date {
    color: var(--text-muted);
    font-size: 0.8rem;
    white-space: nowrap;
}
.dark-table .td-link a {
    color: var(--accent) !important;
    text-decoration: none;
    font-weight: 600;
    white-space: nowrap;
}
.dark-table .td-link a:hover {
    text-decoration: underline;
}
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

/* 시스템/브라우저 다크모드 + Streamlit system theme 무시하고 앱 내부 라이트 테마 강제 */
html {
    color-scheme: light !important;
}
:root, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp, body {
    color-scheme: light !important;
    /* Streamlit 내장 테마 변수 강제 오버라이드 */
    --background-color: #f4f6f9 !important;
    --secondary-background-color: #ffffff !important;
    --primary-color: #03C75A !important;
    --text-color: #1a1f2e !important;
    --font: "Noto Sans KR", sans-serif !important;
    --secondary-text-color: #5a6478 !important;
    --widget-background-color: #ffffff !important;
    --widget-border-color: #e2e8f0 !important;
}

:root {
    --bg-primary: #f4f6f9;
    --bg-secondary: #ffffff;
    --bg-card: #ffffff;
    --bg-elevated: #f0f3f7;
    --text-primary: #1a1f2e;
    --text-secondary: #5a6478;
    --text-muted: #8a94a6;
    --accent: #03C75A;
    --accent-soft: rgba(3,199,90,0.1);
    --accent-glow: rgba(3,199,90,0.18);
    --border: #e2e8f0;
    --border-soft: #edf1f5;
    --danger: #e03131;
    --warning: #f59f00;
    --info: #1c7ed6;
    --radius: 14px;
    --radius-sm: 10px;
    --shadow: 0 2px 16px rgba(0,0,0,0.06);
}
* { font-family: 'Noto Sans KR', sans-serif !important; }

[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-symbols-outlined,
.material-symbols-rounded,
.material-icons {
    font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Icons", sans-serif !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    -webkit-font-smoothing: antialiased !important;
}

[data-testid="stHeader"] {
    background-color: var(--bg-primary) !important;
    background: var(--bg-primary) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stToolbar"] {
    background: transparent !important;
    color: var(--text-primary) !important;
}
[data-testid="stDecoration"] {
    background: transparent !important;
    display: none !important;
}
header[data-testid="stHeader"] * {
    color: var(--text-primary) !important;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
/* Streamlit이 system dark로 data-theme="dark" 를 붙여도 라이트 스타일 강제 */
[data-theme="dark"],
[data-theme="dark"] [data-testid="stAppViewContainer"],
[data-theme="dark"] [data-testid="stApp"],
[data-theme="dark"] .stApp,
html[data-theme="dark"],
body[data-theme="dark"] {
    color-scheme: light !important;
    --background-color: #f4f6f9 !important;
    --secondary-background-color: #ffffff !important;
    --text-color: #1a1f2e !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}
/* 사이드바 글자색은 개별 요소에만 적용 (셀렉트박스 내부 글자색 덮어쓰지 않음) */

/* 검색어 입력창 — 이중 테두리 제거, 단일 테두리만 */
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div,
[data-testid="stDateInput"] > div > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input,
.stDateInput > div > div > input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background: #ffffff !important;
    color: var(--text-primary) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus {
    border-color: #03C75A !important;
    box-shadow: 0 0 0 2px rgba(3,199,90,0.18) !important;
    outline: none !important;
}

/* 💡 라이트 모드 셀렉트박스: 3번(메인)과 동일하게 — 컨트롤 어두운 배경 + 흰 글자, 목록 흰 배경 + 검정 글자 */
/* Select control (메인 / 사이드바 / 폼 모두 동일 적용) */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
div[data-baseweb="select"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stSidebar"] div[data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stForm"] div[data-baseweb="select"] > div,
[data-testid="stForm"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stForm"] div[data-baseweb="select"] > div {
    background-color: #1a222d !important;
    background: #1a222d !important;
    color: #ffffff !important;
    border: 1px solid #2a3441 !important;
    border-color: #2a3441 !important;
}
/* Text and icons inside select control — 선택된 값 글자 흰색 (사이드바* 규칙보다 우선) */
div[data-baseweb="select"] > div span,
div[data-baseweb="select"] > div > div span,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
[data-testid="stSelectbox"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stForm"] div[data-baseweb="select"] span,
[data-testid="stForm"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stForm"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stForm"] [data-baseweb="select"] span {
    color: #ffffff !important;
}
div[data-baseweb="select"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stSidebar"] div[data-baseweb="select"] svg,
[data-testid="stForm"] div[data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-testid="stForm"] div[data-baseweb="select"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
/* Dropdown popover / menu (portal 로 렌더링되는 목록) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"],
[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #1a1f2e !important;
    border-color: #e2e8f0 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}
/* Options — 목록 글자 검정 */
li[data-baseweb="option"],
li[role="option"],
div[role="option"],
[data-baseweb="menu"] li {
    background-color: #ffffff !important;
    color: #1a1f2e !important;
}
li[data-baseweb="option"] span,
li[role="option"] span,
div[role="option"] span,
[data-baseweb="menu"] li span {
    color: #1a1f2e !important;
}
/* Hover & selected states */
li[data-baseweb="option"]:hover,
li[role="option"]:hover,
div[role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background-color: #f0f3f7 !important;
    color: #03C75A !important;
}
li[data-baseweb="option"]:hover span,
li[role="option"]:hover span,
[data-baseweb="menu"] li:hover span {
    color: #03C75A !important;
}
li[aria-selected="true"],
li[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {
    background-color: #e6f9ef !important;
    color: #03C75A !important;
}
li[aria-selected="true"] span,
li[data-baseweb="option"][aria-selected="true"] span,
li[role="option"][aria-selected="true"] span {
    color: #03C75A !important;
}
/* Ensure sidebar text remains dark (overrides any residual) */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p {
    color: #1a1f2e !important;
}

.stButton > button {
    background: linear-gradient(135deg, #03C75A, #02a84e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px var(--accent-glow) !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #03C75A, #02a84e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
}

[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetric"] label,
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}
[data-testid="stMetricDelta"] {
    color: var(--text-secondary) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm);
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--border);
}
/* 비활성 탭: 어두운 글자 (시스템 다크모드 / data-theme 무시) */
.stTabs [data-baseweb="tab"],
.stTabs button[data-baseweb="tab"],
.stTabs [role="tab"],
.stTabs button[role="tab"],
button[data-baseweb="tab"],
div[role="tab"],
[data-testid="stTabs"] [data-baseweb="tab"],
[data-testid="stTabs"] button {
    background: transparent !important;
    color: #1a1f2e !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div,
.stTabs [data-baseweb="tab"] *,
.stTabs button[data-baseweb="tab"] *,
.stTabs [role="tab"] *,
.stTabs button[role="tab"] *,
button[data-baseweb="tab"] *,
div[role="tab"] *,
[data-testid="stTabs"] [data-baseweb="tab"] *,
[data-testid="stTabs"] button * {
    color: #1a1f2e !important;
}
/* 활성 탭: 초록 배경 + 흰 글자 */
.stTabs [aria-selected="true"],
.stTabs button[aria-selected="true"],
.stTabs [role="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"],
div[role="tab"][aria-selected="true"],
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--accent) !important;
    background-color: #03C75A !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div,
.stTabs [aria-selected="true"] *,
.stTabs button[aria-selected="true"] *,
.stTabs [role="tab"][aria-selected="true"] *,
button[data-baseweb="tab"][aria-selected="true"] *,
div[role="tab"][aria-selected="true"] *,
[data-testid="stTabs"] [aria-selected="true"] * {
    color: #ffffff !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

[data-testid="stDownloadButton"] button,
.stDownloadButton > button,
div[data-testid="stDownloadButton"] button {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #1a1f2e !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover,
.stDownloadButton > button:hover {
    background: #f0f3f7 !important;
    border-color: #cbd5e1 !important;
    color: #1a1f2e !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    transform: none !important;
}

.hero {
    background: linear-gradient(135deg, rgba(3,199,90,0.06) 0%, rgba(3,199,90,0.02) 50%, #fff 100%);
    border: 1px solid rgba(3,199,90,0.18);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
}
.hero h1 {
    color: var(--accent) !important;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
}
.hero p { color: var(--text-secondary) !important; margin: 0; font-size: 0.92rem; }
.sidebar-brand {
    text-align: center;
    padding: 0.8rem 0 1.2rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.sidebar-brand h2 { color: var(--accent) !important; font-size: 1.25rem; font-weight: 700; margin: 0; }
.sidebar-brand p { color: var(--text-muted) !important; font-size: 0.75rem; margin: 0.25rem 0 0; }
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.15rem 1.3rem;
    margin-bottom: 0.85rem;
    box-shadow: var(--shadow);
    transition: border-color 0.2s, box-shadow 0.2s;
}
.news-card:hover {
    border-color: rgba(3,199,90,0.35);
    box-shadow: 0 4px 20px rgba(3,199,90,0.08);
}
.news-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.4rem; line-height: 1.4; }
.news-title a { color: var(--text-primary) !important; text-decoration: none; }
.news-title a:hover { color: var(--accent) !important; }
.news-desc { font-size: 0.88rem; color: var(--text-secondary); line-height: 1.55; margin-bottom: 0.65rem; }
.news-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem 1rem;
    align-items: center;
}
.news-meta a { color: var(--accent) !important; text-decoration: none; font-weight: 500; }
.badge {
    display: inline-flex;
    align-items: center;
    background: var(--accent-soft);
    color: var(--accent);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-neutral {
    background: rgba(90,100,120,0.1);
    color: var(--text-secondary);
}
.chip {
    display: inline-block;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    margin: 2px 4px 2px 0;
}
.chip-hot {
    background: var(--accent-soft);
    border-color: rgba(3,199,90,0.3);
    color: var(--accent);
    font-weight: 600;
}
.insight-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    height: 100%;
    box-shadow: var(--shadow);
}
.insight-box h4 {
    margin: 0 0 0.5rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.footer-note { font-size: 0.72rem; text-align: center; opacity: 0.5; margin-top: 1rem; }
.empty-state { text-align: center; padding: 3rem 1rem; color: var(--text-secondary); }
.empty-state .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

.light-table-wrap {
    width: 100%;
    max-height: 420px;
    overflow: auto;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: #ffffff;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.light-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    color: #1a1f2e;
    background: #ffffff;
}
.light-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f0f3f7;
    color: #1a1f2e;
    font-weight: 600;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #e2e8f0;
    white-space: nowrap;
}
.light-table tbody td {
    padding: 10px 12px;
    border-bottom: 1px solid #edf1f5;
    vertical-align: top;
    color: #1a1f2e;
    background: #ffffff;
}
.light-table tbody tr:hover td {
    background: #f4f6f9;
}
.light-table .td-idx {
    color: #8a94a6;
    font-variant-numeric: tabular-nums;
}
.light-table .td-title {
    font-weight: 500;
    max-width: 280px;
}
.light-table .td-desc {
    color: #5a6478;
    max-width: 360px;
}
.light-table .td-domain {
    color: #5a6478;
    font-size: 0.8rem;
}
.light-table .td-date {
    color: #8a94a6;
    font-size: 0.8rem;
    white-space: nowrap;
}
.light-table .td-link a {
    color: #03C75A !important;
    text-decoration: none;
    font-weight: 600;
    white-space: nowrap;
}
.light-table .td-link a:hover {
    text-decoration: underline;
}
</style>
"""

# ═══════════════════════════════════════════════════════════
#  SESSION
# ═══════════════════════════════════════════════════════════
def init_session():
    defaults = {
        "theme": "dark",
        "news_df": pd.DataFrame(),
        "last_searched": "",
        "total_count": 0,
        "search_query_val": "신세경",
        "search_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

if st.session_state.theme == "dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  API CLIENT
# ═══════════════════════════════════════════════════════════
class NaverNewsAPIClient:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID", "")
        self.client_secret = os.environ.get("CLIENT_SECRET", "")

    def _headers(self):
        return {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
        }

    def search_news(self, query: str, display: int = 20, sort: str = "sim"):
        url = (
            "https://naverapihub.apigw.ntruss.com/search/v1/news?"
            + urllib.parse.urlencode(
                {"query": query, "display": display, "start": 1, "sort": sort}
            )
        )
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    total = data.get("total", 0)
                    items = data.get("items", [])
                    df = pd.DataFrame(items)
                    if not df.empty:
                        for col in ("title", "description"):
                            clean = (
                                df[col]
                                .str.replace("<b>", "", regex=False)
                                .str.replace("</b>", "", regex=False)
                                .str.replace("&quot;", '"', regex=False)
                                .str.replace("&amp;", "&", regex=False)
                                .str.replace("&lt;", "<", regex=False)
                                .str.replace("&gt;", ">", regex=False)
                            )
                            df[f"clean_{col if col != 'description' else 'desc'}"] = clean
                        df["source_domain"] = df["link"].apply(_extract_domain)
                        df["date_parsed"] = pd.to_datetime(
                            df["pubDate"], errors="coerce"
                        )
                    return df, total
        except urllib.error.HTTPError as e:
            code = e.code
            msgs = {
                401: "인증 실패 (401): API Key ID / API Key를 확인하세요.",
                403: "권한 오류 (403): NCP에서 API 권한을 확인하세요.",
                404: "엔드포인트 오류 (404): 요청 URL을 확인하세요.",
            }
            st.error(f"❌ {msgs.get(code, f'API 오류: HTTP {code}')}")
        except Exception as e:
            st.error(f"❌ 검색 실패: {e}")
        return pd.DataFrame(), 0


def _extract_domain(url: str) -> str:
    try:
        host = urllib.parse.urlparse(url).netloc
        return host.replace("www.", "") if host else "unknown"
    except Exception:
        return "unknown"


def _env_mtime():
    try:
        return str(_ENV_PATH.stat().st_mtime)
    except Exception:
        return "0"


@st.cache_data(ttl=300)
def run_news_search(query, display, sort, _env_ts=""):
    return NaverNewsAPIClient().search_news(query, display, sort)


# ═══════════════════════════════════════════════════════════
#  ANALYTICS HELPERS
# ═══════════════════════════════════════════════════════════
_STOPWORDS = {
    "있는", "있다", "하는", "하다", "위해", "통해", "대한", "관련", "이번",
    "지난", "오늘", "내일", "어제", "기자", "뉴스", "보도", "밝혔다", "전했다",
    "따르면", "것으로", "등", "및", "그", "이", "저", "것", "수", "등등",
    "에서", "으로", "이다", "합니다", "했습니다", "했다", "된다", "됐다",
    "같은", "다른", "모든", "가장", "더", "또", "또한", "그리고", "하지만",
}


def extract_keywords(texts, top_n: int = 12):
    bag = []
    for t in texts:
        if not isinstance(t, str):
            continue
        words = re.findall(r"[가-힣]{2,}", t)
        bag.extend(w for w in words if w not in _STOPWORDS)
    return Counter(bag).most_common(top_n)


def relative_time(dt) -> str:
    if pd.isna(dt):
        return ""
    now = datetime.now(dt.tzinfo) if getattr(dt, "tzinfo", None) else datetime.now()
    try:
        delta = now - dt.to_pydatetime().replace(tzinfo=None) if hasattr(dt, "to_pydatetime") else now - dt
    except Exception:
        return str(dt)[:16]
    secs = delta.total_seconds()
    if secs < 60:
        return "방금 전"
    if secs < 3600:
        return f"{int(secs // 60)}분 전"
    if secs < 86400:
        return f"{int(secs // 3600)}시간 전"
    if secs < 86400 * 7:
        return f"{int(secs // 86400)}일 전"
    return dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10]


def _esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><h2>📰 뉴스 인사이트</h2>"
        "<p>Naver News · Real-time Dashboard</p></div>",
        unsafe_allow_html=True,
    )

    toggle_text = "☀️ 라이트 모드" if st.session_state.theme == "dark" else "🌙 다크 모드"
    if st.button(toggle_text, key="theme_toggle", width="stretch"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("<div class='section-label'>검색</div>", unsafe_allow_html=True)

    with st.form(key="search_form"):
        search_input = st.text_input(
            "검색어",
            value=st.session_state.search_query_val,
            placeholder="예) 신세경, AI, 파이썬 …",
            key="search_input_box",
            label_visibility="collapsed",
            width="stretch",
        )

        display_count = st.select_slider(
            "결과 수", options=[10, 20, 30, 50, 100], value=20, key="display_slider"
        )
        
        sort_map = {"정확도": "sim", "최신순": "date"}
        sort_label = st.selectbox("정렬", list(sort_map.keys()), key="sort_select")

        search_btn = st.form_submit_button("🔍 검색하기", width="stretch")

    # 최근 검색 최대 3개 출력 및 클릭 시 즉시 검색 실행
    if st.session_state.search_history:
        st.markdown("<div class='section-label'>최근 검색</div>", unsafe_allow_html=True)
        hist = st.session_state.search_history[-3:][::-1]
        for h in hist:
            if st.button(f"↺ {h}", key=f"hist_{h}", width="stretch"):
                st.session_state.search_query_val = h
                with st.spinner(f"'{h}' 검색 중…"):
                    df, total = run_news_search(
                        h, display_count, sort_map[sort_label], _env_ts=_env_mtime()
                    )
                    st.session_state.news_df = df
                    st.session_state.total_count = total
                    st.session_state.last_searched = h
                st.rerun()

    st.markdown(
        "<p class='footer-note'>Data by Naver Open API<br>© 2026 PyLab</p>",
        unsafe_allow_html=True,
    )

# ── 검색 실행 (폼 제출 또는 엔터 입력 시) ───────────────────
if search_btn:
    q = search_input.strip()
    if not q:
        st.sidebar.warning("검색어를 입력하세요.")
    else:
        st.session_state.search_query_val = q
        with st.spinner(f"🔍 '{q}' 관련 뉴스 검색 중…"):
            df, total = run_news_search(
                q, display_count, sort_map[sort_label], _env_ts=_env_mtime()
            )
            st.session_state.news_df = df
            st.session_state.total_count = total
            st.session_state.last_searched = q
            hist = st.session_state.search_history
            if q not in hist:
                hist.append(q)
                st.session_state.search_history = hist[-10:]

if st.session_state.news_df.empty and not st.session_state.last_searched:
    df, total = run_news_search(
        st.session_state.search_query_val, 20, "sim", _env_ts=_env_mtime()
    )
    st.session_state.news_df = df
    st.session_state.total_count = total
    st.session_state.last_searched = st.session_state.search_query_val

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
df = st.session_state.news_df
last_q = st.session_state.last_searched
total = st.session_state.total_count
is_dark = st.session_state.theme == "dark"
PLOT_BG = "#1a222d" if is_dark else "#ffffff"
PAPER_BG = "#12181f" if is_dark else "#f4f6f9"
FONT_CLR = "#e8edf4" if is_dark else "#1a1f2e"
GRID_CLR = "#2a3441" if is_dark else "#e2e8f0"
ACCENT = "#03C75A"

st.markdown(
    f"<div class='hero'>"
    f"<h1>📰 네이버 뉴스 인사이트</h1>"
    f"<p>검색어 <b style='color:var(--accent)'>« {last_q or '—'} »</b> 에 대한 실시간 뉴스 분석 · "
    f"NCP API Gateway</p>"
    f"</div>",
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        "<div class='empty-state'><div class='icon'>📭</div>"
        f"<p><b>'{last_q}'</b> 검색 결과가 없습니다.<br>다른 검색어를 시도해 보세요.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

n_articles = len(df)
n_sources = df["source_domain"].nunique() if "source_domain" in df.columns else 0
latest_dt = df["date_parsed"].max() if "date_parsed" in df.columns else None
latest_label = relative_time(latest_dt) if latest_dt is not None else "—"

k1, k2, k3, k4 = st.columns(4)
k1.metric("가져온 기사", f"{n_articles:,}")
k2.metric("전체 검색 결과", f"{total:,}")
k3.metric("언론사 수", f"{n_sources}")
k4.metric("최신 기사", latest_label)

tab1, tab2, tab3 = st.tabs(["📰 뉴스 피드", "📊 인사이트", "📋 데이터"])

# ════════════ TAB 1: 뉴스 피드 ════════════
with tab1:
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        domains = ["전체"] + sorted(df["source_domain"].dropna().unique().tolist())
        domain_filter = st.selectbox("언론사 필터", domains, key="domain_filter")
    with fc2:
        keyword_filter = st.text_input(
            "제목/요약 필터", placeholder="키워드로 좁히기…", key="kw_filter"
        )

    view = df.copy()
    if domain_filter != "전체":
        view = view[view["source_domain"] == domain_filter]
    if keyword_filter.strip():
        kw = keyword_filter.strip()
        mask = view["clean_title"].str.contains(kw, case=False, na=False) | view[
            "clean_desc"
        ].str.contains(kw, case=False, na=False)
        view = view[mask]

    st.markdown(
        f"<div class='section-label'>실시간 피드 · {len(view)}건</div>",
        unsafe_allow_html=True,
    )

    if view.empty:
        st.info("필터 조건에 맞는 기사가 없습니다.")
    else:
        for _, row in view.iterrows():
            title = row.get("clean_title", "")
            desc = row.get("clean_desc", "")
            link = row.get("link", "#")
            domain = row.get("source_domain", "")
            rel = relative_time(row.get("date_parsed"))
            pub = row.get("pubDate", "")

            st.markdown(
                f"""
                <div class="news-card">
                    <div class="news-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></div>
                    <div class="news-desc">{desc}</div>
                    <div class="news-meta">
                        <span class="badge-neutral badge">{domain}</span>
                        <span>🕒 {rel or pub}</span>
                        <a href="{link}" target="_blank" rel="noopener">원문 보기 ↗</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ════════════ TAB 2: 인사이트 ════════════
with tab2:
    st.markdown("<div class='section-label'>핵심 인사이트</div>", unsafe_allow_html=True)

    texts = (
        df["clean_title"].fillna("").tolist()
        + df["clean_desc"].fillna("").tolist()
    )
    keywords = extract_keywords(texts, top_n=15)

    c_left, c_right = st.columns([1.2, 1])

    with c_left:
        st.markdown("##### 🔥 주요 키워드")
        if keywords:
            kw_df = pd.DataFrame(keywords, columns=["키워드", "빈도"])
            fig_kw = px.bar(
                kw_df,
                x="빈도",
                y="키워드",
                orientation="h",
                color="빈도",
                color_continuous_scale=["#1a3d2a", ACCENT],
            )
            fig_kw.update_layout(
                plot_bgcolor=PLOT_BG,
                paper_bgcolor=PAPER_BG,
                font=dict(color=FONT_CLR),
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                yaxis=dict(
                    categoryorder="total ascending",
                    gridcolor=GRID_CLR,
                    tickfont=dict(color=FONT_CLR),
                    title=dict(font=dict(color=FONT_CLR)),
                ),
                xaxis=dict(
                    gridcolor=GRID_CLR,
                    tickfont=dict(color=FONT_CLR),
                    title=dict(font=dict(color=FONT_CLR)),
                ),
                coloraxis_showscale=False,
                showlegend=False,
            )
            st.plotly_chart(fig_kw, width="stretch")
        else:
            st.caption("키워드를 추출할 수 없습니다.")

        if keywords:
            chips = "".join(
                f'<span class="chip {"chip-hot" if i < 3 else ""}">{w} ({c})</span>'
                for i, (w, c) in enumerate(keywords[:10])
            )
            st.markdown(chips, unsafe_allow_html=True)

    with c_right:
        st.markdown("##### 🏛 언론사 분포")
        if "source_domain" in df.columns:
            src = (
                df["source_domain"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            src.columns = ["언론사", "기사수"]
            fig_src = px.pie(
                src,
                values="기사수",
                names="언론사",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Greens_r,
            )
            fig_src.update_layout(
                plot_bgcolor=PLOT_BG,
                paper_bgcolor=PAPER_BG,
                font=dict(color=FONT_CLR),
                height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=True,
                legend=dict(font=dict(size=11, color=FONT_CLR), orientation="h", y=-0.1),
            )
            fig_src.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(fig_src, width="stretch")

        top_src = (
            df["source_domain"].value_counts().index[0]
            if "source_domain" in df.columns and not df.empty
            else "—"
        )
        top_kw = keywords[0][0] if keywords else "—"
        st.markdown(
            f"""
            <div class="insight-box" style="margin-top:0.5rem">
                <h4>한눈에 보기</h4>
                <p style="margin:0.3rem 0;font-size:0.9rem;color:var(--text-secondary)">
                    가장 많이 보도한 매체: <b style="color:var(--accent)">{top_src}</b><br>
                    최다 등장 키워드: <b style="color:var(--accent)">{top_kw}</b><br>
                    검색 전체 규모: <b>{total:,}</b>건 중 상위 {n_articles}건 분석
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-label'>보도량 추이</div>", unsafe_allow_html=True)
    if "date_parsed" in df.columns:
        try:
            daily = (
                df.dropna(subset=["date_parsed"])
                .assign(day=lambda x: x["date_parsed"].dt.date)
                .groupby("day")
                .size()
                .reset_index(name="기사수")
                .sort_values("day")
            )
            if not daily.empty:
                fig_d = go.Figure()
                fig_d.add_trace(
                    go.Scatter(
                        x=daily["day"],
                        y=daily["기사수"],
                        mode="lines+markers",
                        line=dict(color=ACCENT, width=2.5),
                        marker=dict(size=8, color=ACCENT),
                        fill="tozeroy",
                        fillcolor="rgba(3,199,90,0.12)",
                    )
                )
                fig_d.update_layout(
                    plot_bgcolor=PLOT_BG,
                    paper_bgcolor=PAPER_BG,
                    font=dict(color=FONT_CLR),
                    height=280,
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis=dict(gridcolor=GRID_CLR, title="", tickfont=dict(color=FONT_CLR)),
                    yaxis=dict(gridcolor=GRID_CLR, title="기사 수", tickfont=dict(color=FONT_CLR)),
                )
                st.plotly_chart(fig_d, width="stretch")
            else:
                st.caption("날짜 데이터가 부족합니다.")
        except Exception:
            st.caption("보도량 차트를 그리는 중 오류가 발생했습니다.")

# ════════════ TAB 3: 데이터 테이블 ════════════
with tab3:
    st.markdown("<div class='section-label'>전체 데이터</div>", unsafe_allow_html=True)

    view_cols = ["clean_title", "clean_desc", "source_domain", "pubDate", "link"]
    exist = [c for c in view_cols if c in df.columns]
    disp = df[exist].copy()
    disp.rename(
        columns={
            "clean_title": "제목",
            "clean_desc": "요약",
            "source_domain": "언론사",
            "pubDate": "발행일",
            "link": "링크",
        },
        inplace=True,
    )

    is_light = st.session_state.theme == "light"

    rows_html = []
    for i, (_, row) in enumerate(disp.iterrows()):
        title = _esc(row.get("제목", ""))
        desc = _esc(row.get("요약", ""))
        domain = _esc(row.get("언론사", ""))
        pub = _esc(row.get("발행일", ""))
        link = str(row.get("링크", "#"))
        rows_html.append(
            f"<tr>"
            f"<td class='td-idx'>{i}</td>"
            f"<td class='td-title'>{title}</td>"
            f"<td class='td-desc'>{desc}</td>"
            f"<td class='td-domain'>{domain}</td>"
            f"<td class='td-date'>{pub}</td>"
            f"<td class='td-link'><a href='{_esc(link)}' target='_blank' rel='noopener'>열기 ↗</a></td>"
            f"</tr>"
        )

    table_class_wrap = "light-table-wrap" if is_light else "dark-table-wrap"
    table_class = "light-table" if is_light else "dark-table"

    table_html = f"""
    <div class="{table_class_wrap}">
      <table class="{table_class}">
        <thead>
          <tr>
            <th style="width:48px">#</th>
            <th>제목</th>
            <th>요약</th>
            <th style="width:140px">언론사</th>
            <th style="width:160px">발행일</th>
            <th style="width:72px">링크</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    csv = disp.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSV 다운로드",
        data=csv,
        file_name=f"naver_news_{last_q}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv", 
        width="content"
    )