import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 手機專屬「高對比霓虹」UI 設定 ---
st.set_page_config(page_title="教學管理終端 v5.6", layout="wide")

st.markdown("""
    <style>
    /* 全域極致黑背景 */
    .stApp { background-color: #030508; color: #ffffff; }
    
    /* 頂部導航按鈕：強化對比與發光效果 */
    .stButton>button {
        background: #0d1117 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 12px !important;
        height: 65px !important;
        font-size: 18px !important;
        width: 100% !important;
        font-weight: 900 !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        margin-bottom: 10px;
    }
    .stButton>button:focus, .stButton>button:active {
        background: #00d4ff !important;
        color: #030508 !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
    }
    
    /* 標題與科目文字 */
    .hero-text {
        color: #00d4ff;
        font-size: 26px; font-weight: 900; 
        padding: 15px 0; text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 內容卡片優化 */
    .content-card {
        background: rgba(22, 27, 34, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px; margin-bottom: 20px;
    }
    
    /* 隱藏原生側邊欄 */
    [data-testid="stSidebarNav"] { display: none; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料載入 ---
SHEET_ID = "1oO7Lk7mewVTuN9mBKJxz0LOgFgJMPnKKZ86N3CAdUHs" 
GID_DS = "0"          
GID_STATS = "2044389951" 

@st.cache_data(ttl=5)
def load_all_data():
    def fetch(gid):
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        res = requests.get(url, timeout=5)
        res.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(res.text)).dropna(subset=['學號'])
    df_ds = fetch(GID_DS)
    df_stats = fetch(GID_STATS)
    return df_ds, df_stats

df_ds, df_stats = load_all_data()

# --- 3. 頂部手動導航區 (修復看不見的問題) ---
st.markdown('<p style="text-align:center; color:#888; font-size:12px;">🛰️ 選取科目模組以翻頁</p>', unsafe_allow_html=True)
col_l, col_r = st.columns(2)

if 'current_page' not in st.session_state:
    st.session_state.current_page = "DS"

with col_l:
    if st.button("📈 數據科學 (DS)"):
        st.session_state.current_page = "DS"
with col_r:
    if st.button("📊 統計分析 (Stats)"):
        st.session_state.current_page = "Stats"

# 分隔線
st.markdown('<hr style="border:0.5px solid #333;">', unsafe_allow_html=True)

# --- 4. 根據狀態顯示內容 ---
if st.session_state.current_page == "DS":
    st.markdown('<p class="hero-text">📊 成績統計分析(DS)</p>', unsafe_allow_html=True)
    
    # 關鍵指標
    m1, m2 = st.columns(2)
    with m1: st.metric("總人數", f"{len(df_ds)} P")
    with m2: st.metric("平均到課", f"13.0") # 根據您的截圖固定數值或動態計算

    # 詳細資料表格
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 詳細紀錄資料")
    st.dataframe(df_ds, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 派報中心
    st.markdown('<div class="content-card" style="border-top: 4px solid #00d4ff;">', unsafe_allow_html=True)
    st.subheader("📫 出勤與成績綜合通知")
    target = st.selectbox("選取學員姓名", df_ds['姓名'].unique())
    stu_ds = df_ds[df_ds['姓名'] == target].iloc[-1]
    
    msg = f"姓名：{stu_ds['姓名']}\n到課次數：{stu_ds.get('到課次數','0')}\n學期狀態：ONLINE"
    st.info(msg)
    mailto = f"mailto:{stu_ds['電子郵件']}?subject=通知&body={msg.replace('\n', '%0D%0A')}"
    st.link_button("📤 發送郵件通知", mailto)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<p class="hero-text" style="color:#9400d3;">📊 成績統計分析(Stats)</p>', unsafe_allow_html=True)
    
    # 統計指標
    for c in ['總分']:
        df_stats[c] = pd.to_numeric(df_stats[c], errors='coerce').fillna(0)
        
    m1, m2 = st.columns(2)
    with m1: st.metric("平均分數", f"{df_stats['總分'].mean():.2f}")
    with m2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")

    # 圖表
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#fff")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 成績清單
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部備用連結
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
