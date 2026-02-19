import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# --- CONFIGURATION ---
ST_BALANCE = 100.0
# ใส่ Google Sheet Web App URL ตรงนี้
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzfkmozOhWspXIQWodh6IuH4d1IiTuxeN9oAk0T-lRoKWXeXIU8pbfu3vfKuvH5Igg/exec"

st.set_page_config(
    page_title="$100 Challenge Pro Edition",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM UI / CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #050505;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
    }
    
    /* Card Styling */
    .metric-card {
        background: rgba(30, 30, 30, 0.4);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom Buttons */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    
    /* Hide Streamlit Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'trades' not in st.session_state:
    st.session_state.trades = []

# --- FUNCTIONS ---
def add_trade(trade_data):
    st.session_state.trades.insert(0, trade_data)
    st.toast("บันทึกข้อมูลสำเร็จ 📝", icon="✅")

def sync_data():
    if not GOOGLE_SHEET_URL:
        st.error("กรุณาใส่ GOOGLE_SHEET_URL ในโค้ด")
        return
    try:
        payload = json.dumps(st.session_state.trades)
        requests.post(GOOGLE_SHEET_URL, data=payload)
        st.toast("Sync กับ Google Sheets สำเร็จ! ☁️", icon="🚀")
    except Exception as e:
        st.error(f"Sync ล้มเหลว: {e}")

# --- SIDEBAR: CALCULATOR ---
with st.sidebar:
    st.markdown("### 🧮 Professional Calculator")
    net_pnl = sum([t['pnl'] for t in st.session_state.trades])
    cur_balance = ST_BALANCE + net_pnl
    
    risk_pct = st.number_input("Risk (%)", value=2.0, step=0.5)
    sl_pips = st.number_input("Stop Loss (Pips)", value=20)
    pip_val = st.number_input("Pip Value (per lot)", value=10.0)
    
    risk_amt = cur_balance * (risk_pct / 100)
    recommended_lot = risk_amt / (sl_pips * pip_val) if sl_pips > 0 else 0
    
    st.divider()
    st.markdown(f"**Recommended Lot:**")
    st.markdown(f"## {recommended_lot:.2f}")
    st.caption(f"Risk Amount: ${risk_amt:.2f}")

# --- HEADER SECTION ---
head_col1, head_col2 = st.columns([2, 1])
with head_col1:
    st.markdown("<h1 style='margin-bottom: 0;'>$100 Challenge <span style='color: #4F46E5;'>Pro</span></h1>", unsafe_allow_html=True)
    st.caption("ELEVATE YOUR TRADING PERFORMANCE JOURNAL")

with head_col2:
    st.write("") # Spacer
    st.write("") # Spacer
    sync_btn = st.button("🔄 Sync to Database", use_container_width=True)
    if sync_btn:
        sync_data()

# --- SUMMARY STATS ---
total_trades = len(st.session_state.trades)
wins = len([t for t in st.session_state.trades if t['pnl'] >= 0])
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
avg_pnl = net_pnl / total_trades if total_trades > 0 else 0

st.write("") # Spacer
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"""<div class='metric-card'>
        <p style='color: #888; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;'>Current Balance</p>
        <h2 style='color: #fff; margin:0;'>${cur_balance:.2f}</h2>
        <p style='color: #10b981; font-size: 0.8rem;'>{((cur_balance-100)/100)*100:+.1f}% Growth</p>
    </div>""", unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""<div class='metric-card'>
        <p style='color: #888; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;'>Win Rate</p>
        <h2 style='color: #fff; margin:0;'>{win_rate:.1f}%</h2>
        <p style='color: #888; font-size: 0.8rem;'>{wins} Wins / {total_trades - wins} Loss</p>
    </div>""", unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""<div class='metric-card'>
        <p style='color: #888; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;'>Net Profit</p>
        <h2 style='color: {"#10b981" if net_pnl >= 0 else "#ef4444"}; margin:0;'>${net_pnl:+.2f}</h2>
        <p style='color: #888; font-size: 0.8rem;'>Avg: ${avg_pnl:.2f} / Trade</p>
    </div>""", unsafe_allow_html=True)

with m_col4:
    # Daily Risk Limits
    daily_limit = cur_balance * 0.15
    st.markdown(f"""<div class='metric-card' style='border: 1px solid rgba(239, 68, 68, 0.2);'>
        <p style='color: #ef4444; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;'>Daily Risk Limit</p>
        <h2 style='color: #fff; margin:0;'>${daily_limit:.2f}</h2>
        <p style='color: #888; font-size: 0.8rem;'>Max 15% Drawdown</p>
    </div>""", unsafe_allow_html=True)

# --- EQUITY CHART ---
st.write("")
if total_trades > 0:
    df = pd.DataFrame(st.session_state.trades)
    balance_history = [ST_BALANCE]
    current_bal = ST_BALANCE
    for p in reversed(df['pnl'].tolist()):
        current_bal += p
        balance_history.append(current_bal)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(balance_history))), 
        y=balance_history,
        mode='lines+markers',
        name='Equity',
        line=dict(color='#4F46E5', width=4),
        fill='tozeroy',
        fillcolor='rgba(79, 70, 229, 0.1)'
    ))
    
    fig.update_layout(
        title="Equity Growth Curve",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True)

# --- MAIN CONTENT TABS ---
tab1, tab2, tab3 = st.tabs(["📝 New Journal Entry", "📜 Trade History", "📊 Insights"])

with tab1:
    with st.container():
        st.write("")
        with st.form("trade_form", clear_on_submit=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            date = f_col1.date_input("Date", datetime.now())
            pair = f_col2.text_input("Asset (e.g., XAUUSD, EURUSD)").upper()
            t_type = f_col3.selectbox("Trade Type", ["Buy", "Sell"])
            
            f_col4, f_col5, f_col6 = st.columns(3)
            entry_p = f_col4.number_input("Entry Price", format="%.5f")
            exit_p = f_col5.number_input("Exit Price", format="%.5f")
            pnl_val = f_col6.number_input("Net Profit/Loss (USD)", format="%.2f")
            
            psycho = st.select_slider("Trading Psychology", options=["Panic", "Fear", "Neutral", "Calm", "Focused"])
            notes = st.text_area("Trading Notes / Lesson Learned")
            
            if st.form_submit_button("Log Performance"):
                if pair:
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
                else:
                    st.warning("กรุณาระบุชื่อคู่เงิน")

with tab2:
    st.write("")
    if total_trades > 0:
        display_df = pd.DataFrame(st.session_state.trades)
        
        # คัดกรองคอลัมน์และจัดแต่ง
        def color_status(val):
            color = '#10b981' if val == 'Win' else '#ef4444'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            display_df[["date", "pair", "type", "pnl", "psychology", "status", "notes"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No trades logged yet. Start your journey in the 'New Entry' tab.")

with tab3:
    st.write("")
    if total_trades > 0:
        c_in1, c_in2 = st.columns(2)
        
        # Psychology Distribution
        psycho_df = pd.DataFrame(st.session_state.trades)['psychology'].value_counts().reset_index()
        fig_pie = px.pie(psycho_df, values='count', names='psychology', title="Psychology Distribution", hole=0.4)
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        c_in1.plotly_chart(fig_pie, use_container_width=True)
        
        # Asset Performance
        asset_df = pd.DataFrame(st.session_state.trades).groupby('pair')['pnl'].sum().reset_index()
        fig_bar = px.bar(asset_df, x='pair', y='pnl', title="PnL by Asset", color='pnl', 
                         color_continuous_scale='RdYlGn')
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        c_in2.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("Need data to generate insights.")

# --- FOOTER ---
st.write("")
st.divider()
f_col1, f_col2 = st.columns(2)
f_col1.caption("© 2024 $100 Challenge Pro Edition | Stay Disciplined.")
f_col2.markdown("<p style='text-align: right; font-size: 0.8rem; color: #555;'>Built with Streamlit & Plotly</p>", unsafe_allow_html=True)
