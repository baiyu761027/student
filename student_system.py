import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 極致科技卡片風 UI 設定 ---
st.set_page_config(page_title="學員管理終端 v5.0", layout="wide")

st.markdown("""
    <style>
    /* 全域極致黑背景 */
    .stApp { background-color: #030508; color: #e1e4e8; }
    
    /* 霓虹標題漸層 */
    .hero-text {
        background: linear-gradient(135deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; padding: 25px 0;
        filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.4));
    }

    /* 科技感指標卡片 */
    div[data-testid="stMetric"] {
        background: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: 0.4s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-8px);
        border-color: #00d4ff !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.3);
    }

    /* 內容容器卡片 */
    .content-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(148, 0, 211, 0.15);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }

    /* 霓虹邊框按鈕 */
    .stButton>button {
        background: transparent !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        padding: 12px 30px !important;
        transition: 0.5s;
    }
    .stButton>button:hover {
        background: #00d4ff !important;
        color: #030508 !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.7);
    }

    /* 側邊欄視覺 */
    section[data-testid="stSidebar"] { background-color: #0a0c10 !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料鏈結 (根據您的截圖) ---
SHEET_ID = "1oO7Lk7mewVTuN9mBKJxz0LOgFgJMPnKKZ86N3CAdUHs" 
GID_DS = "0"          # DS分頁
GID_STATS = "2044389951" # Statistics分頁

@st.cache_data(ttl=5)
def load_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'
        data = pd.read_csv(io.StringIO(response.text))
        data.columns = data.columns.str.strip()
        return data.dropna(subset=['學號'])
    except:
        return pd.DataFrame()

# --- 3. 側邊導覽選單 (優化命名) ---
st.sidebar.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:bold; letter-spacing:2px;">🌌 TERMINAL HUB</p>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "請選擇分析模組", 
    ["📈 成績統計分析(DS)", "📈 成績統計分析(Statistics)"],
    index=0
)

st.markdown(f'<p class="hero-text">{page}</p>', unsafe_allow_html=True)

# --- 4. 邏輯模組：DS 分頁 ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        # 頂部視覺卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Enrollment", f"{len(df)} 👤")
        with m2: st.metric("Avg. Attendance", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f}")
        with m3: st.metric("System", "SECURE", delta="SYNC")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📋 學員出勤與報告原始數據")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 郵件通知卡片
        st.markdown('<div class="content-card" style="border-left: 6px solid #00d4ff;">', unsafe_allow_html=True)
        st.subheader("📧 出勤與報告狀況通知")
        target_ds = st.selectbox("搜尋學員發送通知", df['姓名'].unique(), key="ds_mail")
        student_ds = df[df['姓名'] == target_ds].iloc[-1]
        body_ds = f"【出勤通知】\n姓名：{student_ds['姓名']}\n到課：{student_ds.get('到課次數','0')} 次 / 缺席：{student_ds.get('缺席次數','0')} 次\n報告狀態：{student_ds.get('期末報告繳交狀態','未繳')}"
        
        if st.button("🚀 生成通知內容預覽", key="ds_btn"):
            st.code(body_ds)
            mailto_ds = f"mailto:{student_ds['電子郵件']}?subject=出勤狀況通知&body={body_ds.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 發送至 {student_ds['電子郵件']}", mailto_ds)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 邏輯模組：Statistics 分頁 ---
else:
    df = load_data(GID_STATS)
    if not df.empty:
        # 數值處理
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # 指標卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Avg. Score", f"{df['總分'].mean():.2f}")
        with m2: st.metric("Std. Deviation", f"{df['總分'].std():.2f}")
        with m3: st.metric("Top Score", f"{df['總分'].max():.1f}")

        # 統計圖表卡片
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("📈 成績分佈趨勢圖")
            fig = px.histogram(df, x="總分", nbins=12, color_discrete_sequence=['#00d4ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("📊 敘述統計")
            desc = df['總分'].describe().reset_index()
            desc.columns = ['項目', '數值']
            st.dataframe(desc, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 原始數據卡片
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📝 全班學生成績原始清單")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 郵件通知卡片
        st.markdown('<div class="content-card" style="border-left: 6px solid #9400d3;">', unsafe_allow_html=True)
        st.subheader("📧 期中/期末成績通知")
        target_st = st.selectbox("搜尋學員發送成績", df['姓名'].unique(), key="st_mail")
        student_st = df[df['姓名'] == target_st].iloc[-1]
        body_st = f"【成績通知】\n姓名：{student_st['姓名']}\n期中：{student_st['期中考分數']} / 期末：{student_st['期末考分數']}\n總成績：{student_st['總分']}"
        
        if st.button("🚀 生成成績派報預覽", key="st_btn"):
            st.code(body_st)
            mailto_st = f"mailto:{student_st['電子郵件']}?subject=學期成績通知&body={body_st.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 發送至 {student_st['電子郵件']}", mailto_st)
        st.markdown('</div>', unsafe_allow_html=True)

# 底部導航
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND: GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
