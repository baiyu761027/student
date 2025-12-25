import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 深色卡片風格 UI 設定 ---
st.set_page_config(page_title="學員管理終端 v4.0", layout="wide")

st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #05070a; color: #d1d5db; }
    
    /* 霓虹漸層標題 */
    .hero-text {
        background: linear-gradient(90deg, #00d4ff, #9400d3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px; font-weight: 900; padding: 20px 0;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
    }
    
    /* 卡片式數據指標 (Metric Card) */
    div[data-testid="stMetric"] {
        background: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff !important;
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }

    /* 自定義區塊卡片 (Custom Card) */
    .custom-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(148, 0, 211, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    /* 螢光按鈕 */
    .stButton>button {
        background: transparent !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background: #00d4ff !important;
        color: #05070a !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
    }

    /* 表格樣式優化 */
    .stDataFrame {
        border: 1px solid rgba(148, 0, 211, 0.2) !important;
        border-radius: 10px !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結設定 ---
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

st.markdown(f'<p class="hero-text">NEON CARD TERMINAL v4.0</p>', unsafe_allow_html=True)

# --- 4. 頁面邏輯：DS 分頁 ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("總學員數", f"{len(df)} 👤")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f} 次")
        with m3: st.metric("數據鏈結", "ONLINE", delta="穩定")
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 全體學員詳細紀錄清單")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Statistics + 郵件派報 ---
else:
    df = load_data(GID_STATS)
    if not df.empty:
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均總分", f"{df['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df['總分'].max():.1f}")

        st.divider()
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            fig = px.histogram(df, x="總分", title="學員成績分佈圖", color_discrete_sequence=['#00d4ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#d1d5db")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 📈 統計摘要")
            desc = df['總分'].describe().to_frame()
            st.dataframe(desc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- 卡片風格：郵件派報區 ---
        st.markdown('<div class="custom-card" style="border-color:#9400d3;">', unsafe_allow_html=True)
        st.markdown("### 📧 分數郵件派報系統")
        target_name = st.selectbox("選取學員", df['姓名'].unique())
        student = df[df['姓名'] == target_name].iloc[-1]
        
        mail_body = f"""學期成績通知：{student['姓名']} 同學\n學號：{student['學號']}\n期中考：{student['期中考分數']} / 期末考：{student['期末考分數']}\n總分：{student['總分']}"""

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ 預覽派報內容"):
                st.code(mail_body, language="markdown")
        with col2:
            mailto = f"mailto:{student['電子郵件']}?subject=成績通知&body={mail_body.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 發送至 {student['電子郵件']}", mailto)
        st.markdown('</div>', unsafe_allow_html=True)

# 底部工具連結
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
