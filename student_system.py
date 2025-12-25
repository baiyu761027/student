import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. UI 設定 (黑魂科技風) ---
st.set_page_config(page_title="教學管理終端 v2.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #FFFFFF; }
    .hero-text { background: linear-gradient(90deg, #33FF57, #00F2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 800; padding: 15px 0; }
    div[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px !important; }
    .stDataFrame { background: #0d1117 !important; border: 1px solid #30363d !important; }
    .stButton>button { background: linear-gradient(45deg, #33FF57, #00F2FF) !important; color: #000 !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; border: none !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結設定 ---
SHEET_ID = "您的試算表ID"
# 請根據您的 Google Sheets 實際 gid 填寫
GID_DS = "0"          # DS 分頁的 gid
GID_STATS = "123456"  # Statistics 分頁的 gid (請在網址列確認)

@st.cache_data(ttl=5)
def load_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        data = pd.read_csv(io.StringIO(response.text)).dropna(subset=['學號'])
        return data
    except:
        return pd.DataFrame()

# --- 3. 側邊欄導覽 ---
st.sidebar.markdown('<p style="color:#00F2FF; font-size:20px; font-weight:bold;">🛸 導覽選單</p>', unsafe_allow_html=True)
page = st.sidebar.radio("切換管理分頁", ["📄 DS (出勤與報告)", "📈 Statistics (考試統計)"])

# --- 4. 主畫面內容 ---
st.markdown(f'<p class="hero-text">🧬 ACADEMIC TERMINAL - {page.split(" ")[1]}</p>', unsafe_allow_html=True)

if page == "📄 DS (出勤與報告)":
    df_ds = load_data(GID_DS)
    if not df_ds.empty:
        # 指標計算
        total_stu = len(df_ds)
        avg_attend = df_ds['到課次數'].mean()
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("班級總人數", f"{total_stu} 人")
        with m2: st.metric("平均到課次數", f"{avg_attend:.1f}")
        with m3: st.metric("系統狀態", "DS LINKED", delta="SECURE")
        
        st.divider()
        
        col_chart, col_table = st.columns([1, 2.5])
        with col_chart:
            st.markdown("### 🚨 出勤預警")
            # 找出缺席 3 次以上的學員
            warnings = df_ds[df_ds['缺席次數'] >= 3]
            if not warnings.empty:
                for _, row in warnings.iterrows():
                    st.error(f"{row['姓名']} (缺席 {row['缺席次數']} 次)")
            else:
                st.success("目前無出勤異常")
                
        with col_table:
            st.dataframe(df_ds[['班級', '學號', '姓名', '到課次數', '期末報告繳交狀態', '總分']], use_container_width=True, hide_index=True)

elif page == "📈 Statistics (考試統計)":
    df_stats = load_data(GID_STATS)
    if not df_stats.empty:
        # 轉換數值欄位
        for col in ['期中考分數', '期末考分數', '總分']:
            df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce').fillna(0)
            
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均期中分數", f"{df_stats['期中考分數'].mean():.1f}")
        with m2: st.metric("平均期末分數", f"{df_stats['期末考分數'].mean():.1f}")
        with m3: st.metric("全班最高分", f"{df_stats['總分'].max():.1f}")
        
        st.divider()
        
        # 繪製考試分數分佈圖
        fig = px.histogram(df_stats, x="總分", nbins=10, title="學期總分分佈", color_discrete_sequence=['#33FF57'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_stats[['學號', '姓名', '期中考分數', '期末考分數', '考試分數統計', '總分']], use_container_width=True, hide_index=True)

# 底部快捷工具
st.sidebar.divider()
st.sidebar.link_button("📂 開啟 Google Sheets 登錄", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
