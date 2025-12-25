import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 極致科技卡片風 UI ---
st.set_page_config(page_title="學員管理終端 v5.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030508; color: #e1e4e8; }
    .hero-text {
        background: linear-gradient(135deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; padding: 25px 0;
    }
    .content-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(148, 0, 211, 0.2);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetric"] {
        background: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
    }
    /* 強化按鈕視覺 */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #4c1d95) !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
        width: 100%;
        font-weight: bold !important;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結 ---
SHEET_ID = "1oO7Lk7mewVTuN9mBKJxz0LOgFgJMPnKKZ86N3CAdUHs" 
GID_DS = "0"          
GID_STATS = "2044389951" 

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

# --- 3. 側邊導覽 ---
st.sidebar.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:bold;">🌌 系統控制台</p>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "分析科目切換", 
    ["📈 成績統計分析(DS)", "📈 成績統計分析(Statistics)"]
)

st.markdown(f'<p class="hero-text">{page}</p>', unsafe_allow_html=True)

# --- 4. DS 分頁 ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        # 指標卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("總人數", f"{len(df)} P")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f}")
        with m3: st.metric("數據狀態", "ONLINE")

        # 原始資料卡片
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📋 詳細紀錄資料表")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 郵件派報卡片 (固定顯示按鈕)
        st.markdown('<div class="content-card" style="border-top: 4px solid #00d4ff;">', unsafe_allow_html=True)
        st.subheader("📫 出勤通知發送中心")
        target = st.selectbox("選取學員", df['姓名'].unique(), key="ds_sel")
        stu = df[df['姓名'] == target].iloc[-1]
        
        msg = f"同學您好，您的到課次數為：{stu.get('到課次數','0')}次。報告狀態：{stu.get('期末報告繳交狀態','未繳')}"
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👁️ 生成通知預覽", key="ds_pre"):
                st.info(msg)
        with c2:
            mailto = f"mailto:{stu['電子郵件']}?subject=出勤通知&body={msg.replace('\n', '%0D%0A')}"
            st.link_button("📤 直接發送郵件", mailto)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Statistics 分頁 ---
else:
    df = load_data(GID_STATS)
    if not df.empty:
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # 指標卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均成績", f"{df['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df['總分'].max():.1f}")

        # 圖表與原始資料
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📊 成績分佈與原始清單")
        fig = px.histogram(df, x="總分", color_discrete_sequence=['#9400d3'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 郵件派報卡片 (固定顯示按鈕)
        st.markdown('<div class="content-card" style="border-top: 4px solid #9400d3;">', unsafe_allow_html=True)
        st.subheader("📫 成績通知發送中心")
        target_s = st.selectbox("選取學員", df['姓名'].unique(), key="st_sel")
        stu_s = df[df['姓名'] == target_s].iloc[-1]
        
        msg_s = f"同學您好，您的期中考：{stu_s['期中考分數']}分，期末考：{stu_s['期末考分數']}分，總成績：{stu_s['總分']}分。"
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👁️ 生成成績預覽", key="st_pre"):
                st.info(msg_s)
        with c2:
            mailto_s = f"mailto:{stu_s['電子郵件']}?subject=成績通知&body={msg_s.replace('\n', '%0D%0A')}"
            st.link_button("📤 直接發送郵件", mailto_s)
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND: GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
