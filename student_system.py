import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

# --- 1. 科技感 UI 視覺升級 ---
st.set_page_config(page_title="學員管理終端 v3.0", layout="wide")

st.markdown("""
    <style>
    /* 核心背景與文字 */
    .stApp { background-color: #0b0e14; color: #e1e4e8; }
    
    /* 標題漸層：電擊藍到星雲紫 */
    .hero-text {
        background: linear-gradient(90deg, #00f2ff, #7000ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 36px; font-weight: 800; padding: 10px 0;
    }
    
    /* 數據卡片：深色發光邊框 */
    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-top: 3px solid #00f2ff !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    /* 按鈕樣式：霓虹風格 */
    .stButton>button {
        background: linear-gradient(45deg, #00f2ff, #7000ff) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,242,255,0.4); }

    /* 郵件派報框 */
    .mail-preview {
        background: #0d1117;
        border: 1px dashed #7000ff;
        padding: 20px; border-radius: 10px;
        font-family: 'Courier New', monospace;
        color: #00f2ff; margin-top: 15px;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心資料連結 ---
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
st.sidebar.markdown('<p style="color:#00f2ff; font-size:22px; font-weight:bold;">🛰️ SYSTEM NAV</p>', unsafe_allow_html=True)
page = st.sidebar.radio("切換管理分頁", ["📄 學員詳細紀錄 (DS)", "📈 分數統計與派報"])

st.markdown(f'<p class="hero-text">ACADEMIC TERMINAL - v3.0 ({page.split(" ")[1]})</p>', unsafe_allow_html=True)

# --- 4. 頁面邏輯：DS 分頁 ---
if "DS" in page:
    df = load_data(GID_DS)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("班級人數", f"{len(df)} P")
        with m2: st.metric("平均到課", f"{pd.to_numeric(df['到課次數'], errors='coerce').mean():.1f}")
        with m3: st.metric("數據狀態", "STABLE", delta="LINKED")
        
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 5. 頁面邏輯：Statistics + 郵件派報 ---
else:
    df = load_data(GID_STATS)
    if not df.empty:
        # 數值修正
        for c in ['期中考分數', '期末考分數', '總分']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # 頂部統計指標
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("平均總分", f"{df['總分'].mean():.2f}")
        with m2: st.metric("標準差 std", f"{df['總分'].std():.2f}")
        with m3: st.metric("最高分 max", f"{df['總分'].max():.1f}")

        st.divider()
        
        # 分數分佈與敘述統計
        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig = px.histogram(df, x="總分", title="學員總分分佈影響圖", color_discrete_sequence=['#00f2ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e4e8")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("### 📊 敘述統計摘要")
            desc = df['總分'].describe().reset_index()
            desc.columns = ['項目', '數值']
            st.table(desc)

        st.divider()

        # --- 分數郵件派報功能 ---
        st.markdown("### 📧 分數郵件派報中心")
        target_name = st.selectbox("請選擇要發送通知的學生", df['姓名'].unique())
        student = df[df['姓名'] == target_name].iloc[-1]
        
        # 郵件內文自動生成
        mail_body = f"""主題：學期成績通知 - {student['姓名']} 同學
--------------------------------------
親愛的 {student['姓名']} 同學（學號：{student['學號']}）：

本學期您的成績統計如下：
● 期中考分數：{student['期中考分數']}
● 期末考分數：{student['期末考分數']}
● 學期總分數：{student.get('總分', '計算中')}

敘述統計參考：
目前班級平均分為 {df['總分'].mean():.2f}，您的表現優於全班 {len(df[df['總分'] < student['總分']])/len(df)*100:.1f}% 的學員。

如有任何疑問，請於三日內回覆。
--------------------------------------"""

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button(f"🚀 生成 {target_name} 的成績派報"):
                st.markdown(f'<div class="mail-preview">{mail_body.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                st.toast(f"已生成 {target_name} 的發送內容")
        with col_btn2:
            # 建立郵件連結快捷鍵
            mailto_link = f"mailto:{student['電子郵件']}?subject=成績通知&body={mail_body.replace('\n', '%0D%0A')}"
            st.link_button(f"📫 直接發送至 {student['電子郵件']}", mailto_link)

# 底部工具連結
st.sidebar.divider()
st.sidebar.link_button("📂 開啟 Google Sheets 登錄", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
