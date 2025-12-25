import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 深色卡片風格 UI 修正 ---
st.set_page_config(page_title="學員管理終端 v4.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #d1d5db; }
    .hero-text {
        background: linear-gradient(90deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 40px; font-weight: 900; padding: 20px 0;
    }
    /* 卡片容器樣式 */
    .custom-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    /* 指標卡片樣式 */
    div[data-testid="stMetric"] {
        background: #0d1117 !important;
        border: 1px solid rgba(148, 0, 211, 0.3) !important;
        border-radius: 12px !important;
        padding: 15px !important;
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
st.sidebar.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:bold;">🎛️ TERMINAL</p>', unsafe_allow_html=True)
page = st.sidebar.radio("切換視窗", ["📄 學員詳細紀錄 (DS)", "📊 成績統計分析"])

st.markdown(f'<p class="hero-text">NEON CARD TERMINAL v4.1</p>', unsafe_allow_html=True)

# --- 4. 頁面邏輯 ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("總學員數", f"{len(df)} 👤")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f} 次")
        with m3: st.metric("系統狀態", "ONLINE")
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 詳細紀錄清單")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    df = load_data(GID_STATS)
    if not df.empty:
        # 強制轉換數值
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # 指標卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均總分", f"{df['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df['總分'].max():.1f}")

        st.divider()
        
        # 核心內容區 (分左右卡片)
        col_left, col_right = st.columns([1.5, 1])
        
        with col_left:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("📈 成績分佈趨勢")
            fig = px.histogram(df, x="總分", nbins=10, color_discrete_sequence=['#00d4ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#d1d5db")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("📊 敘述統計摘要")
            # 建立結構清晰的統計表
            desc_df = df['總分'].describe().reset_index()
            desc_df.columns = ['統計項目', '數值']
            # 翻譯項目名稱方便閱讀
            name_map = {'count':'人數', 'mean':'平均值', 'std':'標準差', 'min':'最小值', 'max':'最大值', '50%':'中位數'}
            desc_df['統計項目'] = desc_df['統計項目'].replace(name_map)
            st.dataframe(desc_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 郵件派報卡片
        st.markdown('<div class="custom-card" style="border-left: 5px solid #9400d3;">', unsafe_allow_html=True)
        st.subheader("📧 成績郵件派報中心")
        target_name = st.selectbox("選取學員", df['姓名'].unique())
        student = df[df['姓名'] == target_name].iloc[-1]
        
        mail_body = f"成績通知：{student['姓名']}\n學號：{student['學號']}\n總分：{student['總分']}"
        if st.button("🚀 生成派報並預覽"):
            st.info(mail_body)
            mailto = f"mailto:{student['電子郵件']}?subject=成績通知&body={mail_body.replace('\n', '%0D%0A')}"
            st.link_button("📫 發送郵件", mailto)
        st.markdown('</div>', unsafe_allow_html=True)

# 底部工具
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
