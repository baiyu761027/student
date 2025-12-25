import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. UI 風格設定 ---
st.set_page_config(page_title="學員管理終端 v5.3", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030508; color: #e1e4e8; }
    .hero-text {
        background: linear-gradient(135deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; padding: 25px 0;
    }
    .content-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(148, 0, 211, 0.2);
        border-radius: 20px;
        padding: 30px; margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetric"] {
        background: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
    }
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #4c1d95) !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
        width: 100%; font-weight: bold !important;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料連結與跨表處理 ---
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
    # 預先處理成績數值
    for c in ['期中考分數', '期末考分數', '總分']:
        if c in df_stats.columns:
            df_stats[c] = pd.to_numeric(df_stats[c], errors='coerce').fillna(0)
    return df_ds, df_stats

# --- 3. 側邊導覽 ---
df_ds, df_stats = load_all_data()

st.sidebar.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:bold;">🌌 系統控制台</p>', unsafe_allow_html=True)
page = st.sidebar.radio("分析科目切換", ["📈 成績統計分析(DS)", "📈 成績統計分析(Statistics)"])

st.markdown(f'<p class="hero-text">{page}</p>', unsafe_allow_html=True)

# --- 4. DS 分頁邏輯 ---
if "DS" in page:
    if not df_ds.empty:
        # 指標卡片
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("總人數", f"{len(df_ds)} P")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df_ds['到課次數'], errors='coerce').mean():.1f}")
        with m3: st.metric("數據狀態", "SYNCED")

        # 原始資料表格
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📋 詳細紀錄資料表")
        st.dataframe(df_ds, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # DS 郵件派報：加入分數資訊
        st.markdown('<div class="content-card" style="border-top: 4px solid #00d4ff;">', unsafe_allow_html=True)
        st.subheader("📫 出勤與成績綜合通知")
        target = st.selectbox("選取學員", df_ds['姓名'].unique(), key="ds_sel")
        stu_ds = df_ds[df_ds['姓名'] == target].iloc[-1]
        
        # 從 Stats 表中抓取該學生的成績
        stu_score = df_stats[df_stats['學號'] == stu_ds['學號']]
        mid = stu_score['期中考分數'].values[0] if not stu_score.empty else "無資料"
        final = stu_score['期末考分數'].values[0] if not stu_score.empty else "無資料"
        total = stu_score['總分'].values[0] if not stu_score.empty else "無資料"

        msg = f"【學員表現通知】\n姓名：{stu_ds['姓名']}\n學號：{stu_ds['學號']}\n------------------\n到課次數：{stu_ds.get('到課次數','0')} 次\n期中分數：{mid}\n期末分數：{final}\n學期總分：{total}\n------------------\n報告狀態：{stu_ds.get('期末報告繳交狀態','未繳')}"
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👁️ 生成內容預覽", key="ds_pre"): st.info(msg)
        with c2:
            mailto = f"mailto:{stu_ds['電子郵件']}?subject=學員表現通知&body={msg.replace('\n', '%0D%0A')}"
            st.link_button("📤 直接發送郵件", mailto)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Statistics 分頁邏輯 ---
else:
    if not df_stats.empty:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均成績", f"{df_stats['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df_stats['總分'].max():.1f}")

        col_l, col_r = st.columns([1.5, 1])
        with col_l:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("📊 成績分佈圖")
            fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("📝 統計摘要")
            desc = df_stats['總分'].describe().reset_index()
            desc.columns = ['項目', '數值']
            st.dataframe(desc, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📋 全班成績清單")
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Statistics 郵件派報
        st.markdown('<div class="content-card" style="border-top: 4px solid #9400d3;">', unsafe_allow_html=True)
        st.subheader("📫 成績通知發送")
        target_s = st.selectbox("選取學員", df_stats['姓名'].unique(), key="st_sel")
        stu_s = df_stats[df_stats['姓名'] == target_s].iloc[-1]
        msg_s = f"成績通知：{stu_s['姓名']}\n期中：{stu_s['期中考分數']}\n期末：{stu_s['期末考分數']}\n總分：{stu_s['總分']}"
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👁️ 生成成績預覽", key="st_pre"): st.info(msg_s)
        with c2:
            mailto_s = f"mailto:{stu_s['電子郵件']}?subject=成績通知&body={msg_s.replace('\n', '%0D%0A')}"
            st.link_button("📤 直接發送郵件", mailto_s)
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND: GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
