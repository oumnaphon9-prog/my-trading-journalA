import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json

# --- CONFIGURATION ---
ST_BALANCE = 100.0
# ใส่ Google Sheet Web App URL ตรงนี้
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzfkmozOhWspXIQWodh6IuH4d1IiTuxeN9oAk0T-lRoKWXeXIU8pbfu3vfKuvH5Igg/exec"

st.set_page_config(page_title="$100 Challenge Pro", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS เพื่อความสวยงามแบบ Dark Theme
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .metric-card { background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'trades' not in st.session_state:
    # พยายามโหลดข้อมูลจากไฟล์ หรือใช้ข้อมูลว่าง
    st.session_state.trades = []

# --- FUNCTIONS ---
def add_trade(trade_data):
    st.session_state.trades.insert(0, trade_data)
    st.success("บันทึกข้อมูลเรียบร้อย!")

def sync_data():
    if not GOOGLE_SHEET_URL:
        st.error("กรุณาใส่ GOOGLE_SHEET_URL ในโค้ด")
        return
    try:
        # เตรียมข้อมูลสำหรับส่ง (แปลง datetime เป็น string)
        payload = json.dumps(st.session_state.trades)
        requests.post(GOOGLE_SHEET_URL, data=payload)
        st.toast("Sync กับ Google Sheets สำเร็จ!", icon="✅")
    except Exception as e:
        st.error(f"Sync ล้มเหลว: {e}")

# --- SIDEBAR: CALCULATOR ---
with st.sidebar:
    st.header("🧮 Lot Calculator")
    current_balance = ST_BALANCE + sum([t['pnl'] for t in st.session_state.trades])
    risk_pct = st.number_input("Risk (%)", value=2.0)
    sl_pips = st.number_input("Stop Loss (Pips)", value=20)
    pip_val = st.number_input("Pip Value ($)", value=10.0)
    
    risk_amt = current_balance * (risk_pct / 100)
    recommended_lot = risk_amt / (sl_pips * pip_val) if sl_pips > 0 else 0
    
    st.metric("Recommended Lot", f"{recommended_lot:.2f}")
    st.info(f"เสี่ยงครั้งละ: ${risk_amt:.2f}")

# --- MAIN UI ---
st.title("🚀 $100 Challenge Pro")
st.caption("Performance Journal & Risk Management")

col1, col2, col3, col4 = st.columns(4)

# คำนวณ Stats
total_trades = len(st.session_state.trades)
net_pnl = sum([t['pnl'] for t in st.session_state.trades])
cur_balance = ST_BALANCE + net_pnl
wins = len([t for t in st.session_state.trades if t['pnl'] >= 0])
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

with col1:
    st.metric("Balance", f"${cur_balance:.2f}", f"{net_pnl:.2f}")
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with col3:
    st.metric("Total Trades", total_trades)
with col4:
    if st.button("🔄 Sync to Sheets"):
        sync_data()

# --- CHARTS ---
if total_trades > 0:
    df = pd.DataFrame(st.session_state.trades)
    # คำนวณ Balance Curve
    balance_history = [ST_BALANCE]
    current_bal = ST_BALANCE
    for p in reversed(df['pnl'].tolist()):
        current_bal += p
        balance_history.append(current_bal)
    
    fig = px.area(x=list(range(len(balance_history))), y=balance_history, 
                  title="Equity Curve", labels={'x': 'Trades', 'y': 'Balance ($)'})
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- TABS: ENTRY & HISTORY ---
tab1, tab2 = st.tabs(["📝 New Entry", "📜 Trade History"])

with tab1:
    with st.form("trade_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        date = c1.date_input("Date", datetime.now())
        pair = c2.text_input("Pair (เช่น EURUSD)").upper()
        t_type = c3.selectbox("Type", ["Buy", "Sell"])
        
        c4, c5, c6 = st.columns(3)
        entry_p = c4.number_input("Entry Price", format="%.5f")
        exit_p = c5.number_input("Exit Price", format="%.5f")
        pnl_val = c6.number_input("Net PnL (USD)", format="%.2f")
        
        psycho = st.select_slider("Psychology", options=["Fear", "Neutral", "Calm", "Greed"])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Log Trade"):
            new_data = {
                "id": int(datetime.now().timestamp()),
                "date": str(date),
                "pair": pair,
                "type": t_type,
                "entry": entry_p,
                "exit": exit_p,
                "pnl": pnl_val,
                "psychology": psycho,
                "status": "Win" if pnl_val >= 0 else "Loss",
                "notes": notes
            }
            add_trade(new_data)
            st.rerun()

with tab2:
    if total_trades > 0:
        display_df = pd.DataFrame(st.session_state.trades)
        st.dataframe(display_df[["date", "pair", "type", "pnl", "psychology", "status", "notes"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.write("ยังไม่มีประวัติการเทรด")

# --- FOOTER ---
st.divider()
st.caption("ระบบความเสี่ยง: Max Daily Loss $15.00 | Max Drawdown $30.00")
