import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 手機響應式與科技 UI 設定 ---
st.set_page_config(page_title="教學管理終端 v5.4", layout="wide")

st.markdown("""
    <style>
    /* 全域深色背景 */
    .stApp { background-color: #030508; color: #e1e4e8; }
    
    /* 針對手機版的標題優化 */
    .hero-text {
        background: linear-gradient(135deg, #00d4ff, #9400d3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 28px; font-weight: 900; padding: 15px 0;
        text-align: center;
    }
    
    /* 卡片設計 */
    .content-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 15px;
        padding: 20px; margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    /* 手機版按鈕優化：加大觸控面積 */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #4c1d95) !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-size: 18px !important;
        width: 100%; font-weight: bold !important;
        margin-bottom: 10px;
    }

    /* 側邊欄指示器 */
    [data-testid="stSidebarNav"] { padding-top: 20px; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料載入邏輯 ---
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

# --- 3. 側邊導覽 (手機版請點左上角箭頭) ---
st.sidebar.markdown('<p style="color:#00d4ff; font-size:24px; font-weight:bold;">🌌 系統控制台</p>', unsafe_allow_html=True)
st.sidebar.info("📱 手機用戶：選完後請點選右上角『X』回到主畫面")
page = st.sidebar.radio("分析科目切換", ["📈 成績統計分析(DS)", "📈 成績統計分析(Statistics)"])

# 主標題顯示
st.markdown(f'<p class="hero-text">{page}</p>', unsafe_allow_html=True)

# --- 4. DS 分頁內容 ---
if "DS" in page:
    m1, m2 = st.columns(2)
    with m1: st.metric("總人數", f"{len(df_ds)} P")
    with m2: st.metric("平均到課", f"{pd.to_numeric(df_ds['到課次數'], errors='coerce').mean():.1f}")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 詳細紀錄資料")
    st.dataframe(df_ds, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card" style="border-top: 4px solid #00d4ff;">', unsafe_allow_html=True)
    st.subheader("📫 出勤與成績綜合通知")
    target = st.selectbox("選取學員", df_ds['姓名'].unique(), key="ds_sel")
    stu_ds = df_ds[df_ds['姓名'] == target].iloc[-1]
    
    # 關聯成績
    stu_score = df_stats[df_stats['學號'] == stu_ds['學號']]
    mid = stu_score['期中考分數'].values[0] if not stu_score.empty else "N/A"
    final = stu_score['期末考分數'].values[0] if not stu_score.empty else "N/A"
    total = stu_score['總分'].values[0] if not stu_score.empty else "N/A"

    msg = f"姓名：{stu_ds['姓名']}\n到課：{stu_ds.get('到課次數','0')}次\n期中：{mid} / 期末：{final}\n總分：{total}"
    
    if st.button("🚀 生成預覽"): st.info(msg)
    mailto = f"mailto:{stu_ds['電子郵件']}?subject=學員通知&body={msg.replace('\n', '%0D%0A')}"
    st.link_button("📤 直接發送郵件", mailto)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Statistics 分頁內容 ---
else:
    m1, m2 = st.columns(2)
    with m1: st.metric("平均成績", f"{df_stats['總分'].mean():.2f}")
    with m2: st.metric("最高分", f"{df_stats['總分'].max():.1f}")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 分佈與統計")
    fig = px.histogram(df_stats, x="總分", color_discrete_sequence=['#9400d3'])
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 成績清單")
    st.dataframe(df_stats, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-card" style="border-top: 4px solid #9400d3;">', unsafe_allow_html=True)
    target_s = st.selectbox("選取學員", df_stats['姓名'].unique(), key="st_sel")
    stu_s = df_stats[df_stats['姓名'] == target_s].iloc[-1]
    msg_s = f"成績通知：{stu_s['姓名']}\n期中：{stu_s['期中考分數']} / 期末：{stu_s['期末考分數']}\n總分：{stu_s['總分']}"
    
    if st.button("🚀 生成成績預覽"): st.info(msg_s)
    mailto_s = f"mailto:{stu_s['電子郵件']}?subject=成績通知&body={msg_s.replace('\n', '%0D%0A')}"
    st.link_button("📤 直接發送郵件", mailto_s)
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.link_button("📂 BACKEND SHEET", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
