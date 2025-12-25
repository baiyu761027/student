import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. UI 設定 ---
st.set_page_config(page_title="教學管理終端 v2.3", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #FFFFFF; }
    .hero-text { background: linear-gradient(90deg, #33FF57, #00F2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 800; padding: 15px 0; }
    div[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px !important; }
    .stDataFrame { background: #0d1117 !important; border: 1px solid #30363d !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結設定 ---
SHEET_ID = "1JjnIVHXruwhHSBvZGJE_aaLMK1da8uhKu_0fbRhnyDI" 
GID_DS = "0"          
GID_STATS = "2044389951" # ← 已更新為您提供的正確 ID

@st.cache_data(ttl=5)
def load_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            return f"Error: 無法連線至 Google Sheets (代碼 {response.status_code})"
        
        # 讀取並清除欄位名稱前後的空格
        data = pd.read_csv(io.StringIO(response.text))
        data.columns = data.columns.str.strip()
        
        if data.empty:
            return "Error: 分頁內沒有資料"
        return data
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. 側邊欄與頁面切換 ---
st.sidebar.markdown('<p style="color:#00F2FF; font-size:20px; font-weight:bold;">🛸 導覽選單</p>', unsafe_allow_html=True)
page = st.sidebar.radio("功能切換", ["📄 DS (出勤與報告)", "📈 Statistics (成績分析)"])

st.markdown(f'<p class="hero-text">🧬 ACADEMIC TERMINAL - {page.split(" ")[1]}</p>', unsafe_allow_html=True)

# 讀取當前分頁資料
target_gid = GID_DS if "DS" in page else GID_STATS
df_result = load_data(target_gid)

if isinstance(df_result, str):
    st.error(df_result)
else:
    df = df_result
    
    if page == "📄 DS (出勤與報告)":
        # 顯示 DS 內容
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    elif page == "📈 Statistics (成績分析)":
        # 檢查關鍵欄位是否存在
        if '總分' in df.columns:
            # 數值轉換
            for col in ['期中考分數', '期末考分數', '總分']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 頂部統計指標
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("平均總分", f"{df['總分'].mean():.2f}")
            with m2: st.metric("標準差", f"{df['總分'].std():.2f}")
            with m3: st.metric("全班最高分", f"{df['總分'].max():.1f}")
            
            st.divider()
            
            col_chart, col_stats = st.columns([1.5, 1])
            with col_chart:
                fig = px.histogram(df, x="總分", nbins=10, title="學期成績分佈圖", color_discrete_sequence=['#33FF57'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_stats:
                st.markdown("### 📊 敘述統計")
                # 建立敘述統計表格
                desc = df['總分'].describe().reset_index()
                desc.columns = ['項目', '數值']
                st.table(desc)
                
            st.markdown("### 📋 詳細分數清單")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"找不到「總分」欄位。目前偵測到的欄位有：{', '.join(df.columns)}")

st.sidebar.divider()
st.sidebar.link_button("📂 開啟 Google Sheets", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
