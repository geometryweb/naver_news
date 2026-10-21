# ============================================================
# 네이버 오픈 API 실시간 검색 대시보드 (NCP API Gateway 방식)
# naver_dashboard.py
# ============================================================
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

# 스크립트 위치 기준으로 .env 절대 경로 지정 (실행 디렉토리가 달라도 안전)
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

# ── 페이지 기본 설정 ──────────────────────────
st.set_page_config(
    page_title="네이버 검색 대시보드",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 다크 테마 CSS ──────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
:root {
    --bg-primary:#0d1117;--bg-secondary:#161b22;--bg-card:#21262d;
    --text-primary:#e6edf3;--text-secondary:#8b949e;
    --accent:#03C75A;--accent-glow:rgba(3,199,90,0.3);
    --border:#30363d;--shadow:0 8px 32px rgba(0,0,0,0.4);
}
* { font-family:'Noto Sans KR',sans-serif !important; }
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],.main {
    background:var(--bg-primary) !important; color:var(--text-primary) !important; }
[data-testid="stSidebar"] { background:var(--bg-secondary) !important; border-right:1px solid var(--border); }
[data-testid="stSidebar"] * { color:var(--text-primary) !important; }
.stTextInput>div>div>input,.stDateInput>div>div>input {
    background:var(--bg-card) !important; color:var(--text-primary) !important;
    border:1px solid var(--border) !important; border-radius:10px !important; }
.stButton>button {
    background:linear-gradient(135deg,#03C75A,#02a84e) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    padding:0.6rem 1.5rem !important; font-weight:700 !important; font-size:1rem !important;
    transition:all 0.25s ease !important; box-shadow:0 4px 15px var(--accent-glow) !important; }
.stButton>button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 25px var(--accent-glow) !important; }
[data-testid="metric-container"] {
    background:var(--bg-card) !important; border:1px solid var(--border) !important;
    border-radius:16px !important; padding:1.2rem !important; box-shadow:var(--shadow) !important;
    transition:transform 0.2s,box-shadow 0.2s; }
[data-testid="metric-container"]:hover { transform:translateY(-3px); box-shadow:0 12px 40px rgba(3,199,90,0.2) !important; }
.section-header { font-size:1.1rem; font-weight:700; color:var(--accent);
    margin:1.5rem 0 0.8rem; padding-bottom:0.4rem; border-bottom:2px solid var(--accent); }
.stTabs [data-baseweb="tab-list"] { background:var(--bg-card) !important; border-radius:12px; gap:4px; padding:4px; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--text-secondary) !important;
    border-radius:10px !important; font-weight:500 !important; }
.stTabs [aria-selected="true"] { background:var(--accent) !important; color:#fff !important; }
.sidebar-logo { text-align:center; padding:1rem 0; margin-bottom:1rem; border-bottom:1px solid var(--border); }
.sidebar-logo h2 { color:var(--accent) !important; font-size:1.4rem; font-weight:700; margin:0; }
.sidebar-logo p { color:var(--text-secondary) !important; font-size:0.8rem; margin:0.3rem 0 0; }
.badge { display:inline-block; background:var(--accent); color:#fff; border-radius:20px;
    padding:2px 10px; font-size:0.75rem; font-weight:700; margin-left:6px; }
.main-header { background:linear-gradient(135deg,#03C75A15,#1a7f4015); border:1px solid #03C75A40;
    border-radius:20px; padding:1.5rem 2rem; margin-bottom:2rem; }
.main-header h1 { color:var(--accent) !important; font-size:2rem; font-weight:700; margin:0; }
.main-header p { color:var(--text-secondary) !important; margin:0.4rem 0 0; font-size:0.95rem; }
.info-box { background:linear-gradient(135deg,#03C75A10,#02a84e10); border:1px solid #03C75A50;
    border-radius:12px; padding:1rem 1.2rem; margin:1rem 0; color:var(--text-primary); font-size:0.9rem; }
div[data-baseweb="select"]>div { background:var(--bg-card) !important; border-color:var(--border) !important; }
div[data-baseweb="select"] span { color:var(--text-primary) !important; }
div[data-baseweb="popover"] { background:var(--bg-card) !important; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg-secondary); }
::-webkit-scrollbar-thumb { background:var(--accent); border-radius:3px; }
</style>
"""

# ── 라이트 테마 CSS ─────────────────────────────
LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
:root {
    --bg-primary:#f8fafb;--bg-secondary:#ffffff;--bg-card:#ffffff;
    --text-primary:#1a1a2e;--text-secondary:#5a6272;
    --accent:#03C75A;--accent-glow:rgba(3,199,90,0.2);
    --border:#e2e8f0;--shadow:0 4px 20px rgba(0,0,0,0.08);
}
* { font-family:'Noto Sans KR',sans-serif !important; }
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],.main {
    background:var(--bg-primary) !important; color:var(--text-primary) !important; }
[data-testid="stSidebar"] { background:var(--bg-secondary) !important; border-right:1px solid var(--border);
    box-shadow:2px 0 12px rgba(0,0,0,0.06); }
[data-testid="stSidebar"] * { color:var(--text-primary) !important; }
.stTextInput>div>div>input,.stDateInput>div>div>input {
    background:var(--bg-primary) !important; color:var(--text-primary) !important;
    border:1.5px solid var(--border) !important; border-radius:10px !important; }
.stButton>button {
    background:linear-gradient(135deg,#03C75A,#02a84e) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    padding:0.6rem 1.5rem !important; font-weight:700 !important; font-size:1rem !important;
    transition:all 0.25s ease !important; box-shadow:0 4px 15px var(--accent-glow) !important; }
.stButton>button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 25px var(--accent-glow) !important; }
[data-testid="metric-container"] {
    background:var(--bg-card) !important; border:1px solid var(--border) !important;
    border-radius:16px !important; padding:1.2rem !important; box-shadow:var(--shadow) !important;
    transition:transform 0.2s,box-shadow 0.2s; }
[data-testid="metric-container"]:hover { transform:translateY(-3px); box-shadow:0 12px 40px var(--accent-glow) !important; }
.section-header { font-size:1.1rem; font-weight:700; color:var(--accent);
    margin:1.5rem 0 0.8rem; padding-bottom:0.4rem; border-bottom:2px solid var(--accent); }
.stTabs [data-baseweb="tab-list"] { background:var(--border) !important; border-radius:12px; gap:4px; padding:4px; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--text-secondary) !important;
    border-radius:10px !important; font-weight:500 !important; }
.stTabs [aria-selected="true"] { background:var(--accent) !important; color:#fff !important; }
.sidebar-logo { text-align:center; padding:1rem 0; margin-bottom:1rem; border-bottom:1px solid var(--border); }
.sidebar-logo h2 { color:var(--accent) !important; font-size:1.4rem; font-weight:700; margin:0; }
.sidebar-logo p { color:var(--text-secondary) !important; font-size:0.8rem; margin:0.3rem 0 0; }
.badge { display:inline-block; background:var(--accent); color:#fff; border-radius:20px;
    padding:2px 10px; font-size:0.75rem; font-weight:700; margin-left:6px; }
.main-header { background:linear-gradient(135deg,#03C75A10,#02a84e08); border:1px solid #03C75A40;
    border-radius:20px; padding:1.5rem 2rem; margin-bottom:2rem; }
.main-header h1 { color:var(--accent) !important; font-size:2rem; font-weight:700; margin:0; }
.main-header p { color:var(--text-secondary) !important; margin:0.4rem 0 0; font-size:0.95rem; }
.info-box { background:linear-gradient(135deg,#03C75A08,#02a84e05); border:1px solid #03C75A40;
    border-radius:12px; padding:1rem 1.2rem; margin:1rem 0; font-size:0.9rem; }
div[data-baseweb="select"]>div { background:var(--bg-primary) !important; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg-primary); }
::-webkit-scrollbar-thumb { background:var(--accent); border-radius:3px; }
</style>
"""

# ── 세션 상태 초기화 ───────────────────────────
def init_session():
    defaults = {
        "theme": "dark",
        "shopping_df": pd.DataFrame(),
        "trend_df": pd.DataFrame(),
        "last_searched": "",
        "total_count": 0,
        "search_query_val": "신세경",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# 테마 CSS 적용
if st.session_state.theme == "dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)


# ── 네이버 API 클라이언트 (NCP API Gateway 방식) ─────
class NaverOpenAPIClient:
    def __init__(self):
        self.client_id     = os.environ.get("CLIENT_ID", "")
        self.client_secret = os.environ.get("CLIENT_SECRET", "")

    def _headers(self):
        # NCP API Gateway 전용 인증 헤더 설정[cite: 1]
        return {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY":    self.client_secret,
        }

    def search_shopping(self, query: str, display: int = 20, sort: str = "sim"):
        # NCP API Gateway 쇼핑 검색 엔드포인트
        url = (
            "https://naverapihub.apigw.ntruss.com/search/v1/shop?"
            + urllib.parse.urlencode({"query": query, "display": display, "start": 1, "sort": sort})
        )
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    data  = json.loads(resp.read().decode("utf-8"))
                    total = data.get("total", 0)
                    items = data.get("items", [])
                    df    = pd.DataFrame(items)
                    if not df.empty:
                        df["clean_title"] = (
                            df["title"]
                            .str.replace("<b>",  "", regex=False)
                            .str.replace("</b>", "", regex=False)
                        )
                        df["lprice"] = pd.to_numeric(df["lprice"], errors="coerce")
                        df["hprice"] = pd.to_numeric(df["hprice"], errors="coerce")
                    return df, total
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 401:
                st.error("❌ 인증 실패 (401): API Key ID 또는 API Key를 확인하세요.")
            elif code == 403:
                st.error("❌ API 권한 오류 (403): 네이버 클라우드 플랫폼에서 해당 API 권한을 확인하세요.")
            elif code == 404:
                st.error("❌ 엔드포인트 오류 (404): 요청 URL을 확인하세요.")
            elif code == 400:
                st.error("❌ 잘못된 요청 (400): 파라미터를 확인하세요.")
            else:
                st.error(f"❌ API 오류: HTTP {code}")
        except Exception as e:
            st.error(f"❌ 검색 실패: {e}")
        return pd.DataFrame(), 0

    def get_shopping_trend(self, start_date, end_date, time_unit, categories, device="", gender=""):
        # NCP API Gateway 데이터랩 쇼핑인사이트 엔드포인트
        url  = "https://naverapihub.apigw.ntruss.com/datalab/v1/shopping/categories"
        body = {"startDate": start_date, "endDate": end_date, "timeUnit": time_unit, "category": categories}
        if device: body["device"] = device
        if gender: body["gender"] = gender
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=self._headers())
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.getcode() == 200:
                    res   = json.loads(resp.read().decode("utf-8"))
                    rows  = []
                    for r in res.get("results", []):
                        for d in r.get("data", []):
                            rows.append({"category_title": r["title"], "period": d["period"], "ratio": d["ratio"]})
                    return pd.DataFrame(rows)
        except Exception as e:
            st.warning(f"데이터랩 API 호출 실패: {e}")
        return pd.DataFrame()


# 캐시 키에 env 파일 mtime을 포함 → .env 변경 시 자동 캐시 무효화
def _env_mtime():
    try:
        return str(_ENV_PATH.stat().st_mtime)
    except Exception:
        return "0"


@st.cache_data(ttl=300)
def run_search(query, display, sort, _env_ts=""):
    return NaverOpenAPIClient().search_shopping(query, display, sort)


@st.cache_data(ttl=600)
def run_trend(start_date, end_date, time_unit, cats_json, device, gender, _env_ts=""):
    return NaverOpenAPIClient().get_shopping_trend(start_date, end_date, time_unit, json.loads(cats_json), device, gender)


# ── 사이드바 ───────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div class='sidebar-logo'><h2>🔍 네이버 검색</h2><p>실시간 상품 & 트렌드 대시보드</p></div>",
        unsafe_allow_html=True,
    )

    # 테마 토글
    theme_icon  = "🌙 다크 모드" if st.session_state.theme == "dark" else "☀️ 라이트 모드"
    toggle_text = "☀️ 라이트로 전환" if st.session_state.theme == "dark" else "🌙 다크로 전환"
    st.markdown(f"**현재 테마:** {theme_icon}")
    if st.button(toggle_text, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.divider()

    # ─ 쇼핑 검색 ─
    st.markdown("<div class='section-header'>🛍️ 쇼핑 검색</div>", unsafe_allow_html=True)

    search_input = st.text_input(
        "검색어 입력",
        value=st.session_state.search_query_val,
        placeholder="예) 신세경",
        key="search_input_box",
        help="클릭하면 전체 선택되어 바로 새 검색어를 입력할 수 있습니다",
    )

    display_count = st.slider("검색 결과 수", 5, 100, 20, 5, key="display_slider")
    sort_map      = {"정확도순": "sim", "최신순": "date", "가격낮은순": "asc", "가격높은순": "dsc"}
    sort_label    = st.selectbox("정렬 기준", list(sort_map.keys()), key="sort_select")
    search_btn    = st.button("🔍 검색하기", key="search_btn", use_container_width=True)

    st.divider()

    # ─ 트렌드 ─
    st.markdown("<div class='section-header'>📈 쇼핑 트렌드</div>", unsafe_allow_html=True)
    trend_start  = st.date_input("시작일", date.today() - timedelta(days=180),
                                  min_value=date(2017, 8, 1), max_value=date.today(), key="t_start")
    trend_end    = st.date_input("종료일", date.today(),
                                  min_value=date(2017, 8, 1), max_value=date.today(), key="t_end")
    time_unit_m  = {"일간": "date", "주간": "week", "월간": "month"}
    device_m     = {"전체": "", "PC": "pc", "모바일": "mo"}
    gender_m     = {"전체": "", "남성": "m", "여성": "f"}
    t_unit_lbl   = st.selectbox("시간 단위", list(time_unit_m.keys()), index=2, key="t_unit")
    t_device_lbl = st.selectbox("기기", list(device_m.keys()), key="t_device")
    t_gender_lbl = st.selectbox("성별", list(gender_m.keys()), key="t_gender")
    trend_btn    = st.button("📊 트렌드 조회", key="trend_btn", use_container_width=True)

    st.divider()
    st.markdown(
        "<p style='font-size:0.75rem;text-align:center;opacity:0.55;'>Powered by NCP API Gateway<br>© 2026 Dashboard</p>",
        unsafe_allow_html=True,
    )

# ── 검색 / 트렌드 실행 ─────────────────────────
if search_btn:
    q = search_input.strip()
    if not q:
        st.sidebar.warning("검색어를 입력하세요.")
    else:
        st.session_state.search_query_val = q
        with st.spinner(f"🔍 '{q}' 검색 중..."):
            df, total = run_search(q, display_count, sort_map[sort_label], _env_ts=_env_mtime())
            st.session_state.shopping_df  = df
            st.session_state.total_count  = total
            st.session_state.last_searched = q

if trend_btn:
    if trend_start >= trend_end:
        st.sidebar.error("종료일은 시작일보다 이후여야 합니다.")
    else:
        CATS = [
            {"name": "패션의류",    "param": ["50000000"]},
            {"name": "화장품/미용", "param": ["50000002"]},
            {"name": "식품",        "param": ["50000008"]},
        ]
        with st.spinner("📈 트렌드 조회 중..."):
            t_df = run_trend(
                trend_start.strftime("%Y-%m-%d"), trend_end.strftime("%Y-%m-%d"),
                time_unit_m[t_unit_lbl], json.dumps(CATS),
                device_m[t_device_lbl], gender_m[t_gender_lbl],
                _env_ts=_env_mtime(),
            )
            st.session_state.trend_df = t_df

# ── 메인 헤더 ──────────────────────────────────
st.markdown(
    "<div class='main-header'>"
    "<h1>🔍 네이버 실시간 검색 대시보드</h1>"
    "<p>NCP API Gateway를 활용한 실시간 쇼핑 검색 &amp; 트렌드 분석 플랫폼</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── 탭 구성 ────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🛍️ 쇼핑 검색 결과", "📈 카테고리 트렌드", "ℹ️ API 사용 안내"])

is_dark  = st.session_state.theme == "dark"
PLOT_BG  = "#21262d" if is_dark else "#ffffff"
PAPER_BG = "#161b22" if is_dark else "#f8fafb"
FONT_CLR = "#e6edf3" if is_dark else "#1a1a2e"
GRID_CLR = "#30363d" if is_dark else "#e2e8f0"


# ════════════════ TAB 1: 쇼핑 검색 결과 ═══════════════
with tab1:
    df     = st.session_state.shopping_df
    last_q = st.session_state.last_searched

    if df.empty and not last_q:
        st.markdown(
            "<div class='info-box'>💡 <strong>좌측 사이드바</strong>에서 검색어를 입력하고 "
            "<strong>🔍 검색하기</strong> 버튼을 클릭하세요.<br>"
            "기본 검색어 <strong>신세경</strong>이 입력되어 있습니다.</div>",
            unsafe_allow_html=True,
        )
    elif df.empty:
        st.warning(f"'{last_q}' 검색 결과가 없습니다.")
    else:
        total = st.session_state.total_count
        st.markdown(
            f"### 🏷️ **'{last_q}'** 검색 결과 <span class='badge'>{len(df)}개</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"총 {total:,}개의 검색 결과 중 상위 {len(df)}개를 표시합니다.")

        # KPI 메트릭
        valid = df["lprice"].dropna()
        valid = valid[valid > 0]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📦 검색 상품 수",   f"{len(df):,}개")
        with c2: st.metric("💰 평균 최저가",     f"₩{int(valid.mean()):,}"  if not valid.empty else "N/A")
        with c3: st.metric("🏷️ 최저 가격",      f"₩{int(valid.min()):,}"   if not valid.empty else "N/A")
        with c4: st.metric("💎 최고 가격",       f"₩{int(valid.max()):,}"   if not valid.empty else "N/A")

        st.markdown("")
        cc1, cc2 = st.columns(2)

        with cc1:
            st.markdown("<div class='section-header'>💰 가격 분포</div>", unsafe_allow_html=True)
            if not valid.empty:
                fig = px.histogram(valid, nbins=20, color_discrete_sequence=["#03C75A"],
                                   labels={"value": "가격 (원)", "count": "상품 수"})
                fig.update_layout(showlegend=False, plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
                                  font_color=FONT_CLR, height=300,
                                  xaxis=dict(gridcolor=GRID_CLR, title="가격 (원)"),
                                  yaxis=dict(gridcolor=GRID_CLR, title="상품 수"),
                                  margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("가격 데이터가 없습니다.")

        with cc2:
            st.markdown("<div class='section-header'>🏪 쇼핑몰별 상품 수 TOP 10</div>", unsafe_allow_html=True)
            if "mallName" in df.columns:
                mc = df["mallName"].value_counts().head(10).reset_index()
                mc.columns = ["쇼핑몰", "상품수"]
                fig = px.bar(mc, x="상품수", y="쇼핑몰", orientation="h", color_discrete_sequence=["#03C75A"])
                fig.update_layout(showlegend=False, plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
                                  font_color=FONT_CLR, height=300,
                                  xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR),
                                  margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True)

        # 카테고리 파이 차트
        if "category1" in df.columns:
            st.markdown("<div class='section-header'>📂 카테고리 분포</div>", unsafe_allow_html=True)
            cat_df = df["category1"].value_counts().reset_index()
            cat_df.columns = ["카테고리", "수량"]
            cat_df = cat_df[cat_df["카테고리"].notna() & (cat_df["카테고리"] != "")]
            if not cat_df.empty:
                fig = px.pie(cat_df, names="카테고리", values="수량",
                             color_discrete_sequence=px.colors.sequential.Greens[::-1], hole=0.4)
                fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font_color=FONT_CLR,
                                  height=380, legend=dict(font=dict(color=FONT_CLR)),
                                  margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True)

        # 쇼핑몰별 평균 최저가
        if "mallName" in df.columns and not valid.empty:
            st.markdown("<div class='section-header'>📊 쇼핑몰별 평균 최저가</div>", unsafe_allow_html=True)
            mp = (df[df["lprice"] > 0].groupby("mallName")["lprice"]
                  .mean().sort_values(ascending=True).head(10).reset_index())
            mp.columns = ["쇼핑몰", "평균최저가"]
            fig = px.bar(mp, x="평균최저가", y="쇼핑몰", orientation="h",
                         color="평균최저가", color_continuous_scale=["#02a84e","#03C75A","#6bde9a"], text="평균최저가")
            fig.update_traces(texttemplate="₩%{x:,.0f}", textposition="outside")
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                              plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font_color=FONT_CLR,
                              height=350, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR),
                              margin=dict(l=10,r=100,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

        # 상품 목록 테이블
        st.markdown("<div class='section-header'>📋 상품 목록</div>", unsafe_allow_html=True)
        view_cols = ["clean_title","lprice","hprice","mallName","brand","category1"]
        exist = [c for c in view_cols if c in df.columns]
        disp  = df[exist].copy()
        disp.rename(columns={"clean_title":"상품명","lprice":"최저가(원)","hprice":"최고가(원)",
                              "mallName":"쇼핑몰","brand":"브랜드","category1":"카테고리"}, inplace=True)
        for pc in ["최저가(원)","최고가(원)"]:
            if pc in disp.columns:
                disp[pc] = disp[pc].apply(lambda x: f"₩{int(x):,}" if pd.notna(x) and x > 0 else "-")
        st.dataframe(disp, use_container_width=True, height=420)


# ════════════════ TAB 2: 카테고리 트렌드 ══════════════
with tab2:
    t_df = st.session_state.trend_df
    if t_df.empty:
        st.markdown(
            "<div class='info-box'>📊 <strong>좌측 사이드바</strong>의 <strong>📈 쇼핑 트렌드</strong> 섹션에서 "
            "날짜와 조건을 설정 후 <strong>📊 트렌드 조회</strong> 버튼을 클릭하세요.<br>"
            "기본으로 <strong>패션의류, 화장품/미용, 식품</strong> 3개 카테고리를 비교합니다.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("### 📈 쇼핑 카테고리 트렌드 분석")
        st.caption("Y축: 최대값 100 기준 상대적 검색/클릭 지수 (절댓값 아님)")

        t_df["period"] = pd.to_datetime(t_df["period"])

        # 라인 차트
        st.markdown("<div class='section-header'>📉 트렌드 라인 차트</div>", unsafe_allow_html=True)
        fig = px.line(t_df, x="period", y="ratio", color="category_title", markers=True,
                      color_discrete_sequence=["#03C75A","#4fc3f7","#ff8a65"],
                      labels={"period":"기간","ratio":"상대적 지수 (MAX=100)","category_title":"카테고리"})
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font_color=FONT_CLR,
                          xaxis=dict(gridcolor=GRID_CLR, title="기간"),
                          yaxis=dict(gridcolor=GRID_CLR, title="상대적 지수 (MAX=100)", range=[0,105]),
                          legend=dict(font=dict(color=FONT_CLR), bgcolor="rgba(0,0,0,0)"),
                          height=420, hovermode="x unified", margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 면적 차트
        st.markdown("<div class='section-header'>📐 트렌드 면적 차트</div>", unsafe_allow_html=True)
        fig2 = px.area(t_df, x="period", y="ratio", color="category_title",
                       color_discrete_sequence=["#03C75A","#4fc3f7","#ff8a65"],
                       labels={"period":"기간","ratio":"상대적 지수","category_title":"카테고리"})
        fig2.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font_color=FONT_CLR,
                           xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR, range=[0,105]),
                           legend=dict(font=dict(color=FONT_CLR), bgcolor="rgba(0,0,0,0)"),
                           height=350, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

        # 통계
        st.markdown("<div class='section-header'>📊 카테고리별 통계</div>", unsafe_allow_html=True)
        stats = t_df.groupby("category_title")["ratio"].agg(["mean","max","min"]).reset_index()
        stats.columns = ["카테고리","평균 지수","최고 지수","최저 지수"]
        for col in ["평균 지수","최고 지수","최저 지수"]:
            stats[col] = stats[col].round(2)
        st.dataframe(stats, use_container_width=True)


# ════════════════ TAB 3: API 사용 안내 ════════════════
with tab3:
    st.markdown("### ℹ️ NCP API Gateway 사용 안내 및 제한 사항")
    ca, cb = st.columns(2)
    with ca:
        st.markdown(
            "<div class='info-box'><strong>🛍️ 쇼핑 검색 API (NCP Gateway)</strong><br>"
            "• 엔드포인트: <code>naverapihub.apigw.ntruss.com/search/v1/shop</code><br>"
            "• 필수 헤더:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- <code>X-NCP-APIGW-API-KEY-ID</code><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- <code>X-NCP-APIGW-API-KEY</code><br>"
            "• 최대 결과: 100개 / 1회 요청</div>",
            unsafe_allow_html=True,
        )
    with cb:
        st.markdown(
            "<div class='info-box'><strong>📈 데이터랩 쇼핑인사이트 API (NCP Gateway)</strong><br>"
            "• 엔드포인트: <code>naverapihub.apigw.ntruss.com/datalab/v1/shopping/categories</code><br>"
            "• 조회 가능 시작: 2017년 8월 1일<br>"
            "• Y축: 최댓값=100 기준 상대 지수</div>",
            unsafe_allow_html=True,
        )
