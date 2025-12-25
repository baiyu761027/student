import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 手機專屬螢光 UI 設定 ---
st.set_page_config(page_title="教學管理終端 v5.5", layout="wide")

st.markdown("""
    <style>
    /* 全域極致黑背景 */
    .stApp { background-color: #030508; color: #e1e4e8; }
    
    /* 頂部導航按鈕樣式 */
    .nav-button {
        display: inline-block;
        width: 100%;
        padding: 15px;
        margin: 5px 0;
        text-align: center;
        border-radius: 12px;
        font-weight: 800;
        cursor: pointer;
        transition: 0.3s;
    }
    
    /* 卡片設計與螢光邊框 */
    .content-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 15px;
        padding: 15px; margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }

    /* 手機版大型發送按鈕 */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #4c1d95) !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
        height: 60px !important;
        font-size: 20px !important;
        width: 100%; font-weight: 900 !important;
    }
    
    /* 隱藏預設的側邊欄箭頭以減少干擾 */
    [data-testid="stSidebarNav"] { display: none; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料鏈結 (根據您的截圖) ---
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
    for c in ['期中考分數', '期末考分數', '總分']:
        if c in df_stats.columns:
            df_stats[c] = pd.to_numeric(df_stats[c], errors='coerce').fillna(0)
    return df_ds, df_stats

df_ds, df_stats = load_all_data()

# --- 3. 頁面頂部導航 (直接取代側邊欄) ---
st.markdown('<p style="color:#00d4ff; font-weight:900; font-size:14px; margin-bottom:0;">🛰️ 快速切換分析分頁</p>', unsafe_allow_html=True)
col_nav1, col_nav2 = st.columns(2)

# 使用 session_state 來紀錄當前頁面
if 'current_page' not in st.session_state:
    st.session_state.current_page = "DS"

with col_nav1:
    if st.button("📈 DS (科目分析)"):
        st.session_state.current_page = "DS"
with col_nav2:
    if st.button("📊 Stats (科目分析)"):
        st.session_state.current_page = "Stats"

# --- 4. 根據選取狀態顯示內容 ---
if st.session_state.current_page == "DS":
    st.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:900;">ACADEMIC TERMINAL - DS</p>', unsafe_allow_html=True)
    
    # 頂部快速指標 (手機版雙列)
    m1, m2 = st.columns(2)
    with m1: st.metric("Enrollment", f"{len(df_ds)} P")
    with m2: st.metric("Avg Attendance", f"{pd.to_numeric(df_ds['到課次數'], errors='coerce').mean():.1f}")

    # 資料卡片
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 詳細紀錄清單")
    st.dataframe(df_ds, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 派報卡片
    st.markdown('<div class="content-card" style="border-top: 4px solid #00d4ff;">', unsafe_allow_html=True)
    st.subheader("📫 出勤與成績派報")
    target = st.selectbox("搜尋學員", df_ds['姓名'].unique())
    stu_ds = df_ds[df_ds['姓名'] == target].iloc[-1]
    stu_score = df_stats[df_stats['學號'] == stu_ds['學號']]
    
    total = stu_score['總分'].values[0] if not stu_score.empty else "N/A"
    msg = f"姓名：{stu_ds['姓名']}\n到課：{stu_ds.get('到課次數','0')}次\n學期總分：{total}"
    
    st.info(msg)
    mailto = f"mailto:{stu_ds['電子郵件']}?subject=通知&body={msg.replace('\n', '%0D%0A')}"
    st.link_button("📤 發送郵件通知", mailto)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<p style="color:#9400d3; font-size:24px; font-weight:900;">ACADEMIC TERMINAL - Stats</p>', unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1: st.metric("Mean Score", f"{df_stats['總分'].mean():.2f}")
    with m2: st.metric("Max Score", f"{df_stats['總分'].max():.1f}")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 成績統計圖表")
    fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 成績原始清單")
    st.dataframe(df_stats, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部備用連結
st.divider()
st.link_button("📂 BACKEND GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
