import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="QuantBot AI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stMetric label { color: #848E9C !important; font-size: 14px; }
    .stMetric div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

STATE_FILE = "bot_durumu.json"
HISTORY_FILE = "gecmis_islemler.json"

def load_data():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
    else:
        state = {
            "balance": 1000.0,
            "btc_safe": True,
            "open_positions": {},
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    else:
        history = []

    return state, history

state, history = load_data()

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("⚡ QuantBot Pro Dashboard")
    st.caption(f"Son Güncelleme: {state.get('last_update', 'Bilinmiyor')} | Canlı Simülasyon (2.0x)")

with col_head2:
    if st.button("🔄 Verileri Yenile", use_container_width=True):
        st.rerun()

open_positions = state.get("open_positions", {})
cash = state.get("balance", 1000.0)
active_margin = len(open_positions) * 100.0
total_nav = cash + active_margin

df_history = pd.DataFrame(history)
if not df_history.empty and 'pnl' in df_history.columns:
    realized_pnl = df_history['pnl'].sum()
    wins = df_history[df_history['pnl'] > 0]
    win_rate = (len(wins) / len(df_history)) * 100
else:
    realized_pnl = 0.0
    win_rate = 0.0

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Toplam Kasa (NAV)", value=f"${total_nav:.2f}", delta=f"${realized_pnl:.2f}")
with m2:
    st.metric(label="Boşta Nakit", value=f"${cash:.2f}")
with m3:
    st.metric(label="Win Rate", value=f"%{win_rate:.1f}", delta=f"{len(df_history)} İşlem")
with m4:
    btc_status = "🟢 GÜVENLİ" if state.get("btc_safe", True) else "🔴 RİSKLİ (Ayı)"
    st.metric(label="BTC Makro Trend", value=btc_status)

st.divider()

st.subheader(f"📌 Açık Pozisyonlar ({len(open_positions)} / 5)")
if open_positions:
    pos_data = []
    for sym, p in open_positions.items():
        pos_data.append({
            "Parite": sym,
            "Giriş": f"${p.get('entry', 0):.4f}",
            "Zirve": f"${p.get('peak', 0):.4f}",
            "TP1": "✅ Alındı" if p.get('tp1_taken', False) else "⏳ Bekleniyor",
            "Tarih": p.get('entry_time', '-')
        })
    st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)
else:
    st.info("Açık pozisyon yok. Bot piyasayı tarıyor...")

st.divider()

col_graph, col_table = st.columns([1, 1])
with col_graph:
    st.subheader("📈 Kasa Gelişim Eğrisi")
    if not df_history.empty and 'pnl' in df_history.columns:
        df_history['cum_pnl'] = df_history['pnl'].cumsum() + 1000.0
        st.line_chart(df_history.set_index('time')['cum_pnl'])
    else:
        st.info("Henüz geçmiş işlem verisi yok.")

with col_table:
    st.subheader("📋 Son İşlemler")
    if not df_history.empty:
        display_cols = ['time', 'symbol', 'reason', 'roi%', 'pnl']
        available_cols = [c for c in display_cols if c in df_history.columns]
        st.dataframe(df_history[available_cols].tail(8).iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Kapanan işlem bulunamadı.")
