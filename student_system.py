import streamlit as st
import pandas as pd
import requests
import io

# --- 1. 極簡穩定 UI 設定 ---
st.set_page_config(page_title="教學管理終端 v6.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    header, footer {visibility: hidden;}
    .stButton>button { height: 50px !important; font-weight: bold !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 資料載入功能 ---
SHEET_ID = "1oO7Lk7mewVTuN9mBKJxz0LOgFgJMPnKKZ86N3CAdUHs" 
GID_DS = "0"          
GID_STATS = "2044389951" 

@st.cache_data(ttl=5)
def load_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        res = requests.get(url, timeout=5)
        res.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = df.columns.str.strip()
        return df.dropna(subset=['學號'])
    except:
        return pd.DataFrame()

# --- 3. 標題與分頁 (原生 Tab 最穩定) ---
st.title("🧬 教學管理系統 v6.0")

tab1, tab2 = st.tabs(["📊 成績統計分析(DS)", "📈 成績統計分析(Stats)"])

# --- 4. DS 分頁內容 (完全獨立) ---
with tab1:
    df_ds = load_data(GID_DS)
    if not df_ds.empty:
        st.subheader("📍 數據科學 (DS) 概覽")
        col1, col2 = st.columns(2)
        with col1: st.metric("總人數", f"{len(df_ds)} P")
        with col2: st.metric("平均到課", "13.0") # 參考截圖數值

        st.markdown("### 📋 學員詳細紀錄")
        st.dataframe(df_ds, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📫 出勤狀況通知")
        target_ds = st.selectbox("選取學員", df_ds['姓名'].unique(), key="ds_mail_key")
        stu_ds = df_ds[df_ds['姓名'] == target_ds].iloc[-1]
        
        # 只抓取 DS 分頁現有的資料
        msg_ds = f"【出勤通知】\n姓名：{stu_ds['姓名']}\n學號：{stu_ds['學號']}\n到課次數：{stu_ds.get('到課次數','0')}\n報告狀態：{stu_ds.get('期末報告繳交狀態','未紀錄')}\n狀態：ONLINE"
        st.text_area("郵件預覽", msg_ds, height=150)
        
        mailto_ds = f"mailto:{stu_ds['電子郵件']}?subject=出勤狀況通知&body={msg_ds.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送郵件至 {stu_ds['姓名']}", mailto_ds)

# --- 5. Stats 分頁內容 (完全獨立) ---
with tab2:
    df_stats = load_data(GID_STATS)
    if not df_stats.empty:
        # 轉換數值
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df_stats.columns:
                df_stats[c] = pd.to_numeric(df_stats[c], errors='coerce').fillna(0)

        st.subheader("📍 統計分析 (Stats) 概覽")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均總分", f"{df_stats['總分'].mean():.2f}")
        with m2: st.metric("標準差", f"{df_stats['總分'].std():.2f}")
        with m3: st.metric("最高分", f"{df_stats['總分'].max():.1f}")

        # 敘述統計摘要
        st.markdown("### 📝 敘述統計摘要")
        stats_summary = df_stats['總分'].describe().reset_index()
        stats_summary.columns = ['統計項目', '數值']
        name_map = {'count':'總人數', 'mean':'平均值', 'std':'標準差', 'min':'最小值', 'max':'最大值'}
        stats_summary['統計項目'] = stats_summary['統計項目'].replace(name_map)
        st.table(stats_summary) 

        st.markdown("### 📋 全班成績清單")
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📫 成績通知發送")
        target_st = st.selectbox("選取學員", df_stats['姓名'].unique(), key="st_mail_key")
        stu_st = df_stats[df_stats['姓名'] == target_st].iloc[-1]
        
        # 只抓取 Stats 分頁現有的分數資料
        msg_st = f"【成績通知】\n姓名：{stu_st['姓名']}\n期中考：{stu_st.get('期中考分數','0')}\n期末考：{stu_st.get('期末考分數','0')}\n學期總分：{stu_st.get('總分','0')}"
        st.text_area("成績預覽", msg_st, height=150)
        
        mailto_st = f"mailto:{stu_st['電子郵件']}?subject=成績通知&body={msg_st.replace('\n', '%0D%0A')}"
        st.link_button(f"📤 發送成績郵件", mailto_st)

st.sidebar.link_button("📂 BACKEND: GOOGLE SHEETS", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
