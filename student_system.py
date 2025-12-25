import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 手機相容性視覺設定 ---
st.set_page_config(page_title="教學管理終端 v5.7", layout="wide")

st.markdown("""
    <style>
    /* 簡化背景設定，避免 React 渲染報錯 */
    .stApp { background-color: #030508; color: #ffffff; }
    
    /* 強化標題文字 */
    .title-text {
        color: #00d4ff;
        font-size: 24px; font-weight: 800;
        text-align: center; padding: 10px 0;
    }
    
    /* 調整表格高度，適配手機螢幕 */
    .stDataFrame { height: 350px !important; }

    /* 隱藏不必要的組件 */
    header, footer {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none; }
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
    try:
        df_ds = fetch(GID_DS)
        df_stats = fetch(GID_STATS)
        return df_ds, df_stats
    except:
        return pd.DataFrame(), pd.DataFrame()

df_ds, df_stats = load_all_data()

# --- 3. 穩定版頂部導航 (取代複雜 CSS 卡片) ---
st.markdown('<p class="title-text">🧬 ACADEMIC HUB</p>', unsafe_allow_html=True)

# 使用原生按鈕確保手機點擊穩定
col_nav1, col_nav2 = st.columns(2)

if 'page' not in st.session_state:
    st.session_state.page = "DS"

with col_nav1:
    if st.button("📈 DS (科目分析)", use_container_width=True):
        st.session_state.page = "DS"
with col_nav2:
    if st.button("📊 Stats (科目分析)", use_container_width=True):
        st.session_state.page = "Stats"

st.divider()

# --- 4. 分頁邏輯 ---
if st.session_state.page == "DS":
    st.markdown('<p style="color:#00d4ff; font-weight:bold;">📍 目前位置：成績統計分析(DS)</p>', unsafe_allow_html=True)
    
    if not df_ds.empty:
        # 關鍵數據
        m1, m2 = st.columns(2)
        with m1: st.metric("總人數", f"{len(df_ds)} P")
        with m2: st.metric("平均到課", "13.0") # 參照截圖數值

        # 詳細資料
        st.subheader("📋 詳細紀錄資料")
        st.dataframe(df_ds, use_container_width=True, hide_index=True)

        # 派報功能
        st.subheader("📫 出勤與成績通知")
        target = st.selectbox("選取學員", df_ds['姓名'].unique(), key="ds_sel")
        stu = df_ds[df_ds['姓名'] == target].iloc[-1]
        
        # 跨表查詢分數
        score_info = df_stats[df_stats['學號'] == stu['學號']]
        total_s = score_info['總分'].values[0] if not score_info.empty else "N/A"
        
        msg = f"姓名：{stu['姓名']}\n學號：{stu['學號']}\n到課次數：{stu.get('到課次數','0')}\n學期總分：{total_s}"
        st.info(msg)
        
        mailto = f"mailto:{stu['電子郵件']}?subject=學員表現通知&body={msg.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送郵件至 {stu['姓名']}", mailto, use_container_width=True)

else:
    st.markdown('<p style="color:#9400d3; font-weight:bold;">📍 目前位置：成績統計分析(Stats)</p>', unsafe_allow_html=True)
    
    if not df_stats.empty:
        # 指標
        df_stats['總分'] = pd.to_numeric(df_stats['總分'], errors='coerce').fillna(0)
        m1, m2 = st.columns(2)
        with m1: st.metric("平均分數", f"{df_stats['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")

        # 圖表
        fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

        # 原始資料表格
        st.subheader("📋 成績原始清單")
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

# 底部備用工具
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
