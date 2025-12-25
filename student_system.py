import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 深色卡片風格 UI 設定 ---
st.set_page_config(page_title="學員管理終端 v4.3", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #d1d5db; }
    .hero-text {
        background: linear-gradient(90deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 40px; font-weight: 900; padding: 20px 0;
    }
    .custom-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetric"] {
        background: #0d1117 !important;
        border: 1px solid rgba(148, 0, 211, 0.3) !important;
        border-radius: 12px !important;
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

st.markdown(f'<p class="hero-text">NEON CARD TERMINAL v4.3</p>', unsafe_allow_html=True)

# --- 4. 頁面邏輯：DS (出勤與報告) ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("總學員數", f"{len(df)} 👤")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f} 次")
        with m3: st.metric("出勤狀態", "MONITORING")
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 學員出勤與報告詳細紀錄")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- DS 專屬：出勤通知功能 ---
        st.markdown('<div class="custom-card" style="border-left: 5px solid #00d4ff;">', unsafe_allow_html=True)
        st.subheader("📧 出勤與報告狀況通知")
        target_name_ds = st.selectbox("選擇學員 (DS)", df['姓名'].unique(), key="ds_select")
        student_ds = df[df['姓名'] == target_name_ds].iloc[-1]
        
        ds_body = f"【出勤與報告通知】\n姓名：{student_ds['姓名']}\n學號：{student_ds['學號']}\n------------------\n目前到課次數：{student_ds.get('到課次數', 'N/A')}\n缺席紀錄：{student_ds.get('缺席次數', '0')}\n報告狀態：{student_ds.get('報告狀況', '無紀錄')}\n\n請保持良好的出席率，如有問題請回信。"
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 生成出勤通知"):
                st.info(ds_body)
        with col2:
            mailto_ds = f"mailto:{student_ds['電子郵件']}?subject=學員出勤狀況通知&body={ds_body.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 發送郵件至 {student_ds['姓名']}", mailto_ds)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 頁面邏輯：Statistics (成績分析) ---
else:
    df = load_data(GID_STATS)
    if not df.empty:
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("班級平均總分", f"{df['總分'].mean():.2f}")
        with m2: st.metric("分數標準差", f"{df['總分'].std():.2f}")
        with m3: st.metric("最高分紀錄", f"{df['總分'].max():.1f}")

        st.divider()
        
        # 1. 統計圖表與摘要
        col_l, col_r = st.columns([1.5, 1])
        with col_l:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            fig = px.histogram(df, x="總分", nbins=10, color_discrete_sequence=['#9400d3'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#d1d5db")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("📊 統計")
            st.dataframe(df['總分'].describe().to_frame(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. 全班成績明細
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📝 全班學生成績明細")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. 成績派報中心
        st.markdown('<div class="custom-card" style="border-left: 5px solid #9400d3;">', unsafe_allow_html=True)
        st.subheader("📧 個別成績通知派報")
        target_name_st = st.selectbox("選擇學員 (成績)", df['姓名'].unique(), key="st_select")
        student_st = df[df['姓名'] == target_name_st].iloc[-1]
        
        st_body = f"【成績通知】\n姓名：{student_st['姓名']}\n學號：{student_st['學號']}\n期中：{student_st['期中考分數']}\n期末：{student_st['期末考分數']}\n總分：{student_st['總分']}"
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 生成成績通知"):
                st.info(st_body)
        with c2:
            mailto_st = f"mailto:{student_st['電子郵件']}?subject=成績通知&body={st_body.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 發送郵件至 {student_st['姓名']}", mailto_st)
        st.markdown('</div>', unsafe_allow_html=True)

# 底部工具
st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
