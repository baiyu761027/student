import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 簡約穩定版設定 ---
st.set_page_config(page_title="教學管理終端 v5.8", layout="wide")

# 移除所有可能導致 React 衝突的自定義 CSS，僅保留最基本的背景設定
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
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
    try:
        return fetch(GID_DS), fetch(GID_STATS)
    except:
        st.error("資料讀取失敗，請檢查 Google Sheets 權限")
        return pd.DataFrame(), pd.DataFrame()

df_ds, df_stats = load_all_data()

# --- 3. 頂部導覽 (改用原生標籤頁組件，最穩定) ---
st.title("🧬 教學管理系統控制台")

# 使用 Streamlit 官方最穩定的 tabs 組件，手機版絕對能切換
tab1, tab2 = st.tabs(["📈 成績統計分析(DS)", "📊 成績統計分析(Stats)"])

# --- 4. DS 分頁內容 ---
with tab1:
    st.header("數據科學 (DS) 概覽")
    if not df_ds.empty:
        col1, col2 = st.columns(2)
        with col1: st.metric("總人數", f"{len(df_ds)} P")
        with col2: st.metric("平均到課", "13.0")

        st.subheader("📋 詳細紀錄資料")
        st.dataframe(df_ds, use_container_width=True)

        st.divider()
        st.subheader("📫 派報中心")
        target_ds = st.selectbox("選取學員發送通知", df_ds['姓名'].unique(), key="ds_select")
        stu = df_ds[df_ds['姓名'] == target_ds].iloc[-1]
        
        # 獲取分數
        score_match = df_stats[df_stats['學號'] == stu['學號']]
        total_s = score_match['總分'].values[0] if not score_match.empty else "N/A"
        
        msg = f"姓名：{stu['姓名']}\n學號：{stu['學號']}\n到課次數：{stu.get('到課次數','0')}\n學期總分：{total_s}"
        st.text_area("郵件預覽內容", msg, height=120)
        
        mailto = f"mailto:{stu['電子郵件']}?subject=學員通知&body={msg.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送郵件至 {stu['姓名']}", mailto, use_container_width=True)

# --- 5. Stats 分頁內容 ---
with tab2:
    st.header("統計分析 (Stats) 概覽")
    if not df_stats.empty:
        df_stats['總分'] = pd.to_numeric(df_stats['總分'], errors='coerce').fillna(0)
        
        col1, col2 = st.columns(2)
        with col1: st.metric("平均成績", f"{df_stats['總分'].mean():.2f}")
        with col2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")

        st.subheader("📊 成績分佈圖")
        fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 成績原始清單")
        st.dataframe(df_stats, use_container_width=True)

st.sidebar.link_button("📂 開啟 Google Sheets", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
