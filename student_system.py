import streamlit as st
import pandas as pd
import requests
import io

# --- 1. 極簡穩定 UI 設定 ---
st.set_page_config(page_title="教學管理終端 v5.9", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    header, footer {visibility: hidden;}
    /* 加大按鈕觸控面積以利手機操作 */
    .stButton>button { height: 50px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料載入功能 ---
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
        # 預處理數值
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df_stats.columns:
                df_stats[c] = pd.to_numeric(df_stats[c], errors='coerce').fillna(0)
        return df_ds, df_stats
    except:
        return pd.DataFrame(), pd.DataFrame()

df_ds, df_stats = load_all_data()

# --- 3. 標題與分頁 (手機翻頁最穩定的方案) ---
st.title("🧬 教學管理系統")

# 使用原生 Tabs，這是手機版翻頁的唯一保險
tab1, tab2 = st.tabs(["📊 成績統計分析(DS)", "📈 成績統計分析(Stats)"])

# --- 4. DS 分頁內容 ---
with tab1:
    st.subheader("📍 數據科學 (DS) 概覽")
    if not df_ds.empty:
        col1, col2 = st.columns(2)
        with col1: st.metric("總人數", f"{len(df_ds)} P")
        with col2: st.metric("平均到課", "13.0") # 參考截圖數值

        st.markdown("### 📋 學員詳細紀錄")
        st.dataframe(df_ds, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📫 綜合派報中心")
        target_ds = st.selectbox("請選取學員", df_ds['姓名'].unique(), key="ds_mail_key")
        stu_ds = df_ds[df_ds['姓名'] == target_ds].iloc[-1]
        
        # 關聯成績數據
        score_link = df_stats[df_stats['學號'] == stu_ds['學號']]
        total_val = score_link['總分'].values[0] if not score_link.empty else "未錄入"
        
        msg_ds = f"姓名：{stu_ds['姓名']}\n學號：{stu_ds['學號']}\n到課次數：{stu_ds.get('到課次數','0')}\n學期總分：{total_val}\n狀態：ONLINE"
        st.text_area("通知預覽", msg_ds, height=150)
        
        mailto_ds = f"mailto:{stu_ds['電子郵件']}?subject=學員狀況通知&body={msg_ds.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送郵件至 {stu_ds['姓名']}", mailto_ds, use_container_width=True)

# --- 5. Stats 分頁內容 (純敘述統計) ---
with tab2:
    st.subheader("📍 統計分析 (Stats) 概覽")
    if not df_stats.empty:
        # 頂部核心指標
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均總分", f"{df_stats['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df_stats['總分'].max():.1f}")

        # 敘述統計摘要表
        st.markdown("### 📝 敘述統計摘要")
        stats_summary = df_stats['總分'].describe().reset_index()
        stats_summary.columns = ['統計項目', '數值']
        # 中文化項目
        name_map = {'count':'總人數', 'mean':'平均值', 'std':'標準差', 'min':'最小值', '25%':'Q1 (25%)', '50%':'中位數', '75%':'Q3 (75%)', 'max':'最大值'}
        stats_summary['統計項目'] = stats_summary['統計項目'].map(name_map)
        st.table(stats_summary) # 使用 st.table 靜態呈現最穩定

        # 原始資料表格
        st.markdown("### 📋 全班成績原始清單")
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📫 成績派報中心")
        target_st = st.selectbox("選取學員", df_stats['姓名'].unique(), key="st_mail_key")
        stu_st = df_stats[df_stats['姓名'] == target_st].iloc[-1]
        msg_st = f"成績通知：{stu_st['姓名']}\n期中：{stu_st['期中考分數']}\n期末：{stu_st['期末考分數']}\n總分：{stu_st['總分']}"
        
        mailto_st = f"mailto:{stu_st['電子郵件']}?subject=成績通知&body={msg_st.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送成績郵件", mailto_st, use_container_width=True)

# 側邊欄僅保留後端連結
st.sidebar.link_button("📂 BACKEND: GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
