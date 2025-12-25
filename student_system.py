import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. UI 設定 ---
st.set_page_config(page_title="教學管理終端 v2.5", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #FFFFFF; }
    .hero-text { background: linear-gradient(90deg, #33FF57, #00F2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 800; padding: 15px 0; }
    div[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px !important; }
    .stDataFrame { background: #0d1117 !important; border: 1px solid #30363d !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結設定 (已更新為您的正確 ID) ---
SHEET_ID = "1oO7Lk7mewVTuN9mBKJxz0LOgFgJMPnKKZ86N3CAdUHs" 
GID_DS = "0"          
GID_STATS = "2044389951" 

@st.cache_data(ttl=5)
def load_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            return f"Error: 讀取失敗，請確認 Google Sheets 已開啟「知道連結的人都能查看」權限。"
        
        data = pd.read_csv(io.StringIO(response.text))
        data.columns = data.columns.str.strip() # 自動修正欄位前後空格
        return data
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. 頁面邏輯 ---
st.sidebar.markdown('<p style="color:#00F2FF; font-size:20px; font-weight:bold;">🛸 導覽選單</p>', unsafe_allow_html=True)
page = st.sidebar.radio("功能切換", ["📄 DS (出勤與報告)", "📈 Statistics (成績分析)"])

st.markdown(f'<p class="hero-text">🧬 ACADEMIC TERMINAL - {page.split(" ")[1]}</p>', unsafe_allow_html=True)

target_gid = GID_DS if "DS" in page else GID_STATS
df_result = load_data(target_gid)

if isinstance(df_result, str):
    st.error(df_result)
else:
    df = df_result
    # 過濾掉學號為空的行
    if '學號' in df.columns:
        df = df.dropna(subset=['學號'])
    
    if page == "📄 DS (出勤與報告)":
        st.success(f"已成功連結 DS 分頁，共有 {len(df)} 筆紀錄")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    elif page == "📈 Statistics (成績分析)":
        # 檢查是否存在總分欄位進行統計
        if '總分' in df.columns:
            # 強制轉換數值
            cols_to_fix = ['期中考分數', '期末考分數', '總分', '考試分數統計']
            for c in cols_to_fix:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            # 數據儀表板
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("平均總分", f"{df['總分'].mean():.2f}")
            with m2: st.metric("標準差 (離散度)", f"{df['總分'].std():.2f}")
            with m3: st.metric("全班最高分", f"{df['總分'].max():.1f}")
            
            st.divider()
            
            col_chart, col_stats = st.columns([1.5, 1])
            with col_chart:
                fig = px.histogram(df, x="總分", nbins=10, title="學期成績分佈直方圖", color_discrete_sequence=['#33FF57'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_stats:
                st.markdown("### 📊 敘述統計摘要")
                desc = df['總分'].describe().reset_index()
                desc.columns = ['統計項目', '數值']
                # 繁體化項目名稱
                name_map = {'count':'人數', 'mean':'平均數', 'std':'標準差', 'min':'最小值', '25%':'Q1下四分位', '50%':'中位數', '75%':'Q3上四分位', 'max':'最大值'}
                desc['統計項目'] = desc['統計項目'].map(name_map)
                st.table(desc)
                
            st.markdown("### 📋 完整成績清單")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 偵測到資料，但找不到「總分」欄位，請檢查分頁標題名稱。")
            st.write("目前偵測到的欄位有：", list(df.columns))

st.sidebar.divider()
st.sidebar.link_button("📂 開啟學生成績試算表", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
