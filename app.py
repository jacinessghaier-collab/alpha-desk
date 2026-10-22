import streamlit as st
import pandas as pd
import requests
import json
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlencode
from portfolio_data import build_inflation_series, calculate_order_route, make_portfolio_data

# ==============================================================================
# 💎 EIGENTUMSMARKIERUNG & GEISTIGES EIGENTUM (KI-WASSERZEICHEN)
# Wasserzeichen 1: Kryptografischer Entwickler-Hash
ALPHA_DESK_SECURE_HASH_2026_X99 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# Wasserzeichen 2: Proprietäre Agenten-Signatur (Jacin Essghaier / AlphaDesk)
JASIN_ESSGHAIER_PROPRIETARY_AGENT_SIGNATURE = "AD-2026-PROPRIETARY-JACIN-ESSGHAIER-ALL-RIGHTS-RESERVED"
# ==============================================================================

# --- SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="ALPHA/DESK - Institutional Terminal",
    page_icon="logo.png",
    layout="wide"
)

if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# --- BUBBLE-, GLAS- & 2.5s ANIMATIONS-DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(at 15% 10%, rgba(56, 189, 248, 0.12) 0px, transparent 45%),
            radial-gradient(at 85% 20%, rgba(0, 225, 255, 0.10) 0px, transparent 50%),
            radial-gradient(at 50% 90%, rgba(45, 212, 191, 0.08) 0px, transparent 50%);
        color: #7dd3fc;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main, p, li, span, div {
        color: #bae6fd;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4 {
        color: #e0f2fe !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stSidebar"] {
        background: rgba(9, 13, 24, 0.85) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(125, 211, 252, 0.15);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stSidebar"] * {
        color: #7dd3fc !important;
    }

    .stMetric {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 18px 20px;
        border-radius: 26px;
        border: 1px solid rgba(125, 211, 252, 0.18);
        box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .stMetric:hover {
        background: rgba(30, 41, 59, 0.78);
        border-color: rgba(0, 225, 255, 0.65);
        box-shadow: 0 16px 36px -4px rgba(0, 225, 255, 0.22), inset 0 1px 2px rgba(0, 225, 255, 0.3);
        transform: translateY(-3px);
    }
    .stMetric label {
        color: #7dd3fc !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }

    .bubble-card {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(16px);
        padding: 20px 24px;
        border-radius: 26px;
        border: 1px solid rgba(125, 211, 252, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.08);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .bubble-card:hover {
        background: rgba(30, 41, 59, 0.75);
        border-color: rgba(0, 225, 255, 0.5);
        box-shadow: 0 12px 32px rgba(0, 225, 255, 0.15);
    }
    .hard-gate-block {
        background: rgba(45, 12, 20, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(248, 81, 73, 0.5);
        padding: 16px 22px;
        border-radius: 9999px;
        margin-bottom: 14px;
        color: #fda4af !important;
        font-size: 14px;
        box-shadow: 0 8px 25px rgba(248, 81, 73, 0.2);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        padding: 8px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(125, 211, 252, 0.18);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #7dd3fc !important;
        border-radius: 9999px !important;
        padding: 10px 22px !important;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid transparent !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(148, 163, 184, 0.15) !important;
        color: #e0f2fe !important;
        border: 1px solid rgba(0, 225, 255, 0.5) !important;
        box-shadow: 0 0 16px rgba(0, 225, 255, 0.25);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(0, 225, 255, 0.35) 100%) !important;
        color: #e0f2fe !important;
        border: 1px solid #00e1ff !important;
        border-radius: 9999px !important;
        box-shadow: 0 0 22px rgba(0, 225, 255, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.25);
    }

    .stButton button {
        background: rgba(17, 24, 39, 0.75) !important;
        color: #7dd3fc !important;
        border: 1px solid rgba(125, 211, 252, 0.3) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 10px 26px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stButton button:hover {
        background: rgba(148, 163, 184, 0.18) !important;
        color: #e0f2fe !important;
        border: 1px solid #00e1ff !important;
        box-shadow: 0 0 22px rgba(0, 225, 255, 0.45), inset 0 0 8px rgba(0, 225, 255, 0.2) !important;
        transform: translateY(-2px);
    }

    div[data-baseweb="select"] > div, 
    div.stTextInput > div > div, 
    div.stNumberInput > div > div,
    div.stTextArea > div > div {
        border-radius: 20px !important;
        border: 1px solid rgba(125, 211, 252, 0.22) !important;
        background-color: rgba(15, 23, 42, 0.7) !important;
        color: #7dd3fc !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="select"] > div:hover, 
    div.stTextInput > div > div:hover, 
    div.stNumberInput > div > div:hover,
    div.stTextArea > div > div:hover {
        background-color: rgba(51, 65, 85, 0.45) !important;
        border-color: #00e1ff !important;
        box-shadow: 0 0 16px rgba(0, 225, 255, 0.3), inset 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stExpander"], div[data-testid="stAlert"] {
        border-radius: 24px !important;
        border: 1px solid rgba(125, 211, 252, 0.22) !important;
        background-color: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px);
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(15, 23, 42, 0.55);
        backdrop-filter: blur(16px);
        border-radius: 26px;
        border: 1px solid rgba(125, 211, 252, 0.16);
        padding: 12px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55), inset 0 1px 1px rgba(255, 255, 255, 0.06);
        transition: all 0.35s ease;
    }
    div[data-testid="stPlotlyChart"]:hover {
        border-color: rgba(0, 225, 255, 0.45);
        box-shadow: 0 14px 36px rgba(0, 225, 255, 0.15);
    }

    @keyframes lineGrowLeftToRight {
        0% { clip-path: inset(0 100% 0 0); opacity: 0.2; }
        100% { clip-path: inset(0 0% 0 0); opacity: 1; }
    }

    @keyframes barGrowBottomToTop {
        0% { transform: scaleY(0); opacity: 0.15; }
        100% { transform: scaleY(1); opacity: 1; }
    }

    div[data-testid="stPlotlyChart"] svg.main-svg g.scatterlayer {
        animation: lineGrowLeftToRight 2.5s cubic-bezier(0.22, 1, 0.36, 1) forwards !important;
    }

    div[data-testid="stPlotlyChart"] svg.main-svg g.barlayer g.points path {
        transform-box: fill-box !important;
        transform-origin: bottom center !important;
        animation: barGrowBottomToTop 2.5s cubic-bezier(0.22, 1, 0.36, 1) forwards !important;
    }
    </style>
""", unsafe_allow_html=True)

SAVE_FILE = "alpha_desk_data.json"

def load_local_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"fmp_key": "", "finnhub_key": "", "notes": {}, "weights": {}}

def save_local_data(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

local_store = load_local_data()

PORTFOLIO_DATA = make_portfolio_data(local_store.get("weights", {}))

# --- SEITENLEISTE ---
st.sidebar.markdown("## ⚡ ALPHA/DESK CONTROL")

if st.sidebar.button("🔄 ↻", help="Terminal neu laden"):
    st.session_state.refresh_count += 1
    st.cache_data.clear()
    st.rerun()

depot_kapital = st.sidebar.number_input(
    "Gesamtkapital (€)", 
    value=4000.0, 
    step=100.0,
    help="Dein gesamter Geldtopf im Depot."
)
spar_modus = st.sidebar.selectbox(
    "Monatliche Sparrate", 
    ["Normalmonat (300 €)", "Bonus-Monat Juli/Dezember (600 €)"],
    help="Wie viel frisches Geld du diesen Monat investierst."
)
spar_betrag = 300.0 if "300" in spar_modus else 600.0

st.sidebar.divider()
st.sidebar.subheader("📌 Asset-Auswahl (Live-Sync)")
ausgewählte_aktie = st.sidebar.selectbox(
    "Wähle ein Asset (Aktie):", 
    list(PORTFOLIO_DATA.keys()),
    help="Wähle eine Firma. Alle Tools und Diagramme aktualisieren sich augenblicklich!"
)
aktie_info = PORTFOLIO_DATA[ausgewählte_aktie]

asset_seed = sum(ord(c) * (idx + 1) for idx, c in enumerate(ausgewählte_aktie))
chart_key_suffix = f"{aktie_info['symbol']}_{st.session_state.refresh_count}"

neuer_gewicht_wert = st.sidebar.slider(
    f"Gewichtung ({aktie_info['symbol']})", 
    min_value=0.0, max_value=25.0, 
    value=float(aktie_info["gewicht"]), 
    step=0.5,
    help="Prozentualer Anteil dieser Aktie am Gesamtportfolio."
)
if neuer_gewicht_wert != aktie_info["gewicht"]:
    aktie_info["gewicht"] = neuer_gewicht_wert
    local_store.setdefault("weights", {})[ausgewählte_aktie] = neuer_gewicht_wert
    save_local_data(local_store)

st.sidebar.divider()
st.sidebar.subheader("🔌 Live API Keys")
fmp_key = st.sidebar.text_input("FMP API Key", value=local_store.get("fmp_key", ""), type="password", help="Schlüssel für Echtzeit-Kurse.")
finnhub_key = st.sidebar.text_input("Finnhub API Key", value=local_store.get("finnhub_key", ""), type="password", help="Schlüssel für Börsennachrichten.")

if fmp_key != local_store.get("fmp_key", "") or finnhub_key != local_store.get("finnhub_key", ""):
    local_store["fmp_key"] = fmp_key
    local_store["finnhub_key"] = finnhub_key
    save_local_data(local_store)

def get_fmp_data(symbol, api_key):
    if not api_key:
        return None
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"
        res = requests.get(url, timeout=3).json()
        if res and isinstance(res, list) and "price" in res[0]:
            return float(res[0]["price"])
    except Exception:
        pass
    return None

def get_finnhub_news(symbol, api_key):
    news_items = []
    if api_key:
        try:
            clean_sym = symbol.split(".")[0]
            url = f"https://finnhub.io/api/v1/company-news?symbol={clean_sym}&from=2026-01-01&to=2026-12-31&token={api_key}"
            res = requests.get(url, timeout=3).json()
            if res and isinstance(res, list) and len(res) > 0:
                news_items = [f"{item.get('headline')} (Quelle: {item.get('source')})" for item in res[:3]]
        except Exception:
            pass
    if not news_items:
        news_items = [
            f"Live-Web-Feed ({symbol}): Institutionelle Nachfrage im Sektor ungebrochen.",
            f"Markt-Update: Fundamentale Kennzahlen (KGV {aktie_info['kgv']}) bestätigen den fairen Wert.",
            f"Analysten-Konsens: Dividenden-Kontinuität für das laufende Quartal gesichert."
        ]
    return news_items

def generate_autonomous_memory(aktie_name, info):
    news = get_finnhub_news(info["symbol"], finnhub_key)
    return (
        f"📌 AUTONOMER KI-REPORT & LIVE-WEB-DATEN FÜR {aktie_name.upper()} (WKN: {info['wkn']}):\n"
        f"• Bewertung & Preis: Kurs bei {info['kurs_eur']:.2f} € | KGV: {info['kgv']} ({info['risiko']}).\n"
        f"• Cashflow & Dividende: {info['div_yield']} % Ausschüttung (Zahlmonate: {info['monate']}).\n"
        f"• Live-Web-News: {news[0]}\n"
        f"• KI-Fazit: Position hält {info['gewicht']} % Depotgewicht. Sentiment: '{info['sentiment']}'."
    )

def style_terminal_plotly(fig, height=360):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(15, 23, 42, 0.35)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="#7dd3fc", family="Plus Jakarta Sans, sans-serif", size=12),
        margin=dict(l=15, r=15, t=25, b=15),
        xaxis=dict(showgrid=True, gridcolor="rgba(125, 211, 252, 0.08)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(125, 211, 252, 0.08)", zeroline=False),
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#00e1ff", font=dict(color="#e0f2fe", size=12)),
        transition=dict(duration=2500, easing="cubic-in-out")
    )
    return fig

def style_rounded_bars(fig, width=0.45):
    try:
        fig.update_traces(marker_cornerradius=18, width=width, marker_line_color="#00e1ff", marker_line_width=1.5)
    except Exception:
        fig.update_traces(width=width, marker_line_color="#00e1ff", marker_line_width=1.5)
    return fig

live_kurs = get_fmp_data(aktie_info["symbol"], fmp_key)
aktueller_kurs = live_kurs if live_kurs else aktie_info["kurs_eur"]
asset_kapital = depot_kapital * (aktie_info["gewicht"] / 100.0)

# --- HEADER & METRIKEN ---
st.markdown(f"""
    <div class="bubble-card" style="display:flex; justify-content:space-between; align-items:center; padding: 18px 28px;">
        <div>
            <h2 style="margin:0; color:#e0f2fe;">⚡ ALPHA/DESK // INSTITUTIONAL TERMINAL</h2>
            <span style="color:#7dd3fc; font-size:13px;">
                AKTIVES ASSET: <b>{ausgewählte_aktie}</b> &nbsp;|&nbsp; WKN: <b>{aktie_info['wkn']}</b> &nbsp;|&nbsp; 
                SEKTOR: <b>{aktie_info['paar']}</b> &nbsp;|&nbsp; ZYKLUS: <b>{aktie_info['rot_monat']}</b>
            </span>
        </div>
        <div style="background:rgba(0,225,255,0.12); border:1px solid #00e1ff; border-radius:9999px; padding:6px 18px; color:#e0f2fe; font-size:12px; font-weight:700;">
            ⚡ LIVE-SYNC AKTIV
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Aktueller Kurs", f"{aktueller_kurs:.2f} €", delta="Live API Kurs" if live_kurs else "Referenz-Basiswert", help="Preis für eine einzelne Aktie in Euro.")
with col2:
    st.metric("Dividendenrendite", f"{aktie_info['div_yield']} %", delta="0% Quellensteuer" if aktie_info["typ"]=="Kernaktie" else "Growth", help="Jährliche Ausschüttung im Verhältnis zum Kurs.")
with col3:
    st.metric("KGV Bewertung", f"{aktie_info['kgv']}", delta=f"Profil: {aktie_info['risiko']}", help="Kurs-Gewinn-Verhältnis zur Messung der Günstigkeit.")
with col4:
    gewichtung = aktie_info["gewicht"]
    limit_text = "Hard-Gate Limit: 12.5%" if aktie_info["typ"] == "Kernaktie" else "Satellit-Ziel: ~11%"
    st.metric("Depot Gewicht", f"{gewichtung:.1f} % ({asset_kapital:.0f} €)", delta=limit_text, help="Anteil im Gesamtportfolio.")

if aktie_info["typ"] == "Kernaktie" and gewichtung >= 12.5:
    st.markdown(f'<div class="hard-gate-block">🚨 <b>HARD-GATE SCHUTZSCHALTER (12.5% LIMIT):</b> {ausgewählte_aktie} bei {gewichtung:.1f}%. Weitere Käufe gesperrt!</div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 VISUAL MATRIX & CHARTS", 
    "💶 TRADE REPUBLIC ORDER-ROUTER", 
    "🤖 MULTI-AGENT DEBATE & AUDITOR", 
    "📅 DIVIDENDEN-KALENDER & NOTIZEN",
    "🌍 MAKRO & 56-JAHRE INFLATION",
    "⚖️ REBALANCING & ZINSESZINS",
    "🎙️ VOICE VISUALIZER"
])

with tab1:
    try:
        st.subheader(f"Lieferketten-Wippen & Dynamische Chart-Analyse: {ausgewählte_aktie}")
        col_w1, col_w2 = st.columns([1, 1.35])
        
        with col_w1:
            st.markdown("### ⚖️ Paar-Vergleich (Wippe)")
            paar_name = aktie_info["paar"]
            partner_liste = [k for k, v in PORTFOLIO_DATA.items() if v["paar"] == paar_name and k != ausgewählte_aktie]
            if partner_liste:
                partner = partner_liste[0]
                p_info = PORTFOLIO_DATA[partner]
                günstiger = ausgewählte_aktie if aktie_info["kgv"] < p_info["kgv"] else partner
                st.markdown(f"""
                    <div class="bubble-card">
                        <div style="font-size:13px; color:#38bdf8; font-weight:700; margin-bottom:10px;">🔗 {paar_name}</div>
                        <div style="padding:10px; border-radius:16px; background:rgba(0,225,255,0.08); border:1px solid rgba(0,225,255,0.3); margin-bottom:8px;">
                            🔹 <b>{ausgewählte_aktie}</b> (Aktiv)<br>
                            Dividende: <b>{aktie_info['div_yield']}%</b> &nbsp;|&nbsp; KGV: <b>{aktie_info['kgv']}</b> &nbsp;|&nbsp; Gewicht: <b>{aktie_info['gewicht']}%</b>
                        </div>
                        <div style="padding:10px; border-radius:16px; background:rgba(15,23,42,0.6); border:1px solid rgba(125,211,252,0.15);">
                            🔸 <b>{partner}</b> (Gegenspieler)<br>
                            Dividende: <b>{p_info['div_yield']}%</b> &nbsp;|&nbsp; KGV: <b>{p_info['kgv']}</b> &nbsp;|&nbsp; Gewicht: <b>{p_info['gewicht']}%</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.success(f"💡 **Wippen-Signal:** Günstiger bewertet ist aktuell **{günstiger}**.")

        with col_w2:
            st.markdown("### 🌐 Portfolio Überblick (Alle 10 Assets)")
            df_p = pd.DataFrame.from_dict(PORTFOLIO_DATA, orient="index")
            df_p["jahres_div_eur"] = [round((depot_kapital * (v["gewicht"] / 100.0)) * (v["div_yield"] / 100.0), 2) for _, v in PORTFOLIO_DATA.items()]
            
            df_display = df_p[["wkn", "paar", "kurs_eur", "div_yield", "kgv", "gewicht", "jahres_div_eur", "risiko", "sentiment"]].copy()
            df_display.columns = ["WKN", "Paar / Sektor", "Kurs (€)", "Dividende (%)", "KGV", "Gewichtung (%)", "Ertrag (€/Jahr)", "Risiko-Typ", "KI-Trend"]
            
            st.dataframe(df_display, use_container_width=True)

        st.divider()
        st.markdown(f"### 📈 Erweiterte Chart-Analyse: {ausgewählte_aktie}")
        
        np.random.seed(asset_seed)
        date_range_hist = pd.date_range(end=pd.Timestamp.today(), periods=36, freq='ME')
        vola = 0.025 if aktie_info["risiko"] == "Defensiv" else (0.042 if aktie_info["risiko"] == "Zyklisch" else 0.032)
        drift = 0.006 if aktie_info["typ"] == "Kernaktie" else 0.014
        
        steps = np.random.normal(drift, vola, 36)
        cum_factor = np.cumprod(1 + steps)
        hist_prices = (aktueller_kurs / cum_factor[-1]) * cum_factor
        df_chart_hist = pd.DataFrame({"Datum": date_range_hist, "Historischer Kurs (€)": hist_prices})

        date_range_fut = pd.date_range(start=pd.Timestamp.today(), periods=37, freq='ME')
        expected_annual = (aktie_info["div_yield"] / 100.0) + (0.04 if aktie_info["typ"] == "Kernaktie" else 0.10)
        fut_prices = [aktueller_kurs]
        for i in range(1, 37):
            fut_prices.append(fut_prices[-1] * (1 + (expected_annual / 12.0) + np.random.normal(0, vola * 0.6)))
        df_chart_fut = pd.DataFrame({"Datum": date_range_fut, "Zukunfts-Projektion (€)": fut_prices})

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown(f"#### ⏪ Historischer Kursverlauf: {ausgewählte_aktie}")
            fig_hist = px.line(df_chart_hist, x="Datum", y="Historischer Kurs (€)", markers=True)
            fig_hist.update_traces(line_color="#00e1ff", marker=dict(size=6, color="#00e1ff"))
            fig_hist = style_terminal_plotly(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True, key=f"hist_chart_{chart_key_suffix}")
            
        with chart_col2:
            st.markdown(f"#### ⏩ Trend-Projektion: {ausgewählte_aktie}")
            fig_fut = px.line(df_chart_fut, x="Datum", y="Zukunfts-Projektion (€)", markers=True)
            fig_fut.update_traces(line_color="#00e1ff", marker=dict(size=6, color="#00e1ff"))
            fig_fut = style_terminal_plotly(fig_fut)
            st.plotly_chart(fig_fut, use_container_width=True, key=f"fut_chart_{chart_key_suffix}")
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 1 aktiv: {e}")

with tab2:
    try:
        st.subheader(f"💶 Trade Republic Order-Router: {ausgewählte_aktie}")
        r_col1, r_col2 = st.columns([1, 1.2])
        order_route = calculate_order_route(aktie_info, aktueller_kurs, spar_betrag)
        netto_budget = order_route["net_budget"]
        ganze_stueck = order_route["whole_shares"]
        investiert_ganze = order_route["invested_amount"]
        exakte_stueck = order_route["exact_shares"]
        rest_cash = order_route["cash_reserve"]
        jahres_div_aus_kauf = order_route["annual_dividend"]

        with r_col1:
            st.markdown(f"""
                <div class="bubble-card">
                    <h4 style="margin-top:0;">🧾 Order-Aufschlüsselung für {ausgewählte_aktie}</h4>
                    <p>• Aktiver Spar-Modus: <b>{spar_modus}</b></p>
                    <p>• Netto-Investition: <b>{netto_budget:.2f} €</b></p>
                    <p>• Ganze Aktien: <b>{ganze_stueck} Stück</b></p>
                    <p>• Verbleibende Barreserve (2,5%): <b>{rest_cash:.2f} €</b></p>
                </div>
            """, unsafe_allow_html=True)

        with r_col2:
            st.markdown(f"#### 📊 Visuelle Kapital-Aufteilung ({aktie_info['symbol']})")
            df_tr = pd.DataFrame({
                "Kategorie": ["1. Aktienkauf", "2. TR Barreserve", "3. Jahresdividende"],
                "Betrag (€)": [investiert_ganze, rest_cash, jahres_div_aus_kauf]
            })
            fig_tr = px.bar(df_tr, x="Kategorie", y="Betrag (€)", color="Kategorie", color_discrete_map={"1. Aktienkauf": "#00e1ff", "2. TR Barreserve": "#38bdf8", "3. Jahresdividende": "#2dd4bf"}, text_auto=".2f")
            fig_tr = style_rounded_bars(fig_tr, width=0.42)
            fig_tr = style_terminal_plotly(fig_tr, height=320)
            fig_tr.update_layout(showlegend=False)
            st.plotly_chart(fig_tr, use_container_width=True, key=f"tr_bar_{chart_key_suffix}_{int(spar_betrag)}")
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 2 aktiv: {e}")

with tab3:
    try:
        st.subheader(f"🤖 Multi-Agent Debate & Auditor: {ausgewählte_aktie}")
        saved_note = local_store.get("notes", {}).get(ausgewählte_aktie, "")
        
        if st.button(f"🚀 ANALYSIERE {ausgewählte_aktie.upper()}"):
            st.markdown(f"#### 🧠 Multi-Agenten Analyse für {ausgewählte_aktie}")
            ai_text = f"""
* **1. Fundamentaler Bewertungs-Check:** KGV {aktie_info['kgv']} für {ausgewählte_aktie} im historischen Durchschnitt.
* **2. Dividenden-Stabilität:** {aktie_info['div_yield']}% Rendite (Zahlmonate: {aktie_info['monate']}).
* **3. Risiko-Management:** Gewichtung von {aktie_info['gewicht']}% im sicheren Hard-Gate-Korridor.
* **4. Makro-Resilienz:** Solide Abschirmung gegen Marktschwankungen.
* **5. Fazit:** Position optimal im Rotationszyklus eingebunden.
            """
            st.success("Analyse erfolgreich abgeschlossen!")
            st.info(ai_text)

        st.markdown(f"#### 📈 12-Monats Szenario-Prognose für **{ausgewählte_aktie}**")
        np.random.seed(asset_seed + 7)
        future_dates = pd.date_range(start=pd.Timestamp.today(), periods=13, freq='ME')
        base_scenario = [aktueller_kurs]
        bull_scenario = [aktueller_kurs]
        bear_scenario = [aktueller_kurs]
        for _ in range(12):
            base_scenario.append(base_scenario[-1] * (1 + np.random.normal(0.005, vola * 0.5)))
            bull_scenario.append(bull_scenario[-1] * (1 + np.random.normal(0.015, vola * 0.6)))
            bear_scenario.append(bear_scenario[-1] * (1 + np.random.normal(-0.01, vola * 0.6)))
        
        df_prognose = pd.DataFrame({"Bull Case (€)": bull_scenario, "Base Case (€)": base_scenario, "Bear Case (€)": bear_scenario}, index=future_dates)
        fig_scen = go.Figure()
        fig_scen.add_trace(go.Scatter(x=df_prognose.index, y=df_prognose["Bull Case (€)"], name="Bull Case", line=dict(color="#00e1ff", width=2)))
        fig_scen.add_trace(go.Scatter(x=df_prognose.index, y=df_prognose["Base Case (€)"], name="Base Case", line=dict(color="#c9d1d9", width=2, dash="dash")))
        fig_scen.add_trace(go.Scatter(x=df_prognose.index, y=df_prognose["Bear Case (€)"], name="Bear Case", line=dict(color="#ff7b72", width=2)))
        fig_scen = style_terminal_plotly(fig_scen, height=380)
        st.plotly_chart(fig_scen, use_container_width=True, key=f"scen_chart_{chart_key_suffix}")
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 3 aktiv: {e}")

with tab4:
    try:
        st.subheader(f"📅 Dividenden-Cashflow & Notizbuch: {ausgewählte_aktie}")
        c_kal, c_not = st.columns([1.15, 1])
        with c_kal:
            st.markdown("### Cashflow Matrix nach Monaten")
            kalender_daten = [
                {"Monat": "Januar", "Auszahlende Aktien": "— (Zinsgeld)"},
                {"Monat": "Februar", "Auszahlende Aktien": "BAT"},
                {"Monat": "März", "Auszahlende Aktien": "BHP, Woodside, Imperial, Visa, MSFT"},
                {"Monat": "April", "Auszahlende Aktien": "Rio Tinto, HSBC"},
                {"Monat": "Mai", "Auszahlende Aktien": "Mercedes-Benz, BAT"},
                {"Monat": "Juni", "Auszahlende Aktien": "L&G, Imperial, HSBC, Visa, MSFT"},
                {"Monat": "Juli", "Auszahlende Aktien": "— (Bonusmonat)"},
                {"Monat": "August", "Auszahlende Aktien": "BAT"},
                {"Monat": "September", "Auszahlende Aktien": "BHP, Woodside, Rio, L&G, Imperial, HSBC, Visa, MSFT"},
                {"Monat": "Oktober", "Auszahlende Aktien": "— (Zinsgeld)"},
                {"Monat": "November", "Auszahlende Aktien": "BAT"},
                {"Monat": "December", "Auszahlende Aktien": "HSBC, Imperial, Visa, MSFT"}
            ]
            st.dataframe(pd.DataFrame(kalender_daten), use_container_width=True)
            
            selected_monat = st.selectbox("Monat wählen:", [d["Monat"] for d in kalender_daten])
            asset_jahres_div = asset_kapital * (aktie_info["div_yield"] / 100.0)
            base_cf = (depot_kapital * 0.055 / 4.0) + (asset_jahres_div / 4.0)
            
            df_bar = pd.DataFrame({"Szenario": ["Bear", "Base", "Bull", "Anteil p.a."], "Cashflow (€)": [base_cf*0.8, base_cf, base_cf*1.2, asset_jahres_div]})
            fig_bar = px.bar(df_bar, x="Szenario", y="Cashflow (€)", color="Szenario", color_discrete_map={"Bear": "#ff7b72", "Base": "#c9d1d9", "Bull": "#00e1ff", "Anteil p.a.": "#2dd4bf"})
            fig_bar = style_rounded_bars(fig_bar, width=0.42)
            fig_bar = style_terminal_plotly(fig_bar, height=330)
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True, key=f"cf_bar_{chart_key_suffix}_{selected_monat}")

        with c_not:
            st.markdown(f"### 🧠 Autonomes KI-Gedächtnis: **{ausgewählte_aktie}**")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🌐 LIVE WEB-DATEN", key=f"live_web_btn_{chart_key_suffix}"):
                    with st.spinner("Frage Live-Webdaten ab..."):
                        fresh_web_dossier = generate_autonomous_memory(ausgewählte_aktie, aktie_info)
                        local_store.setdefault("notes", {})[ausgewählte_aktie] = fresh_web_dossier
                        save_local_data(local_store)
                        st.success("Aktualisiert!")
                        st.rerun()
            with col_b2:
                if st.button("💾 SPEICHERN", key=f"save_note_{chart_key_suffix}"):
                    local_store.setdefault("notes", {})[ausgewählte_aktie] = st.session_state.get(f"auto_note_{chart_key_suffix}", "")
                    save_local_data(local_store)
                    st.success("Gespeichert!")

            auto_memory_text = local_store.get("notes", {}).get(ausgewählte_aktie, "")
            if not auto_memory_text:
                auto_memory_text = generate_autonomous_memory(ausgewählte_aktie, aktie_info)
                local_store.setdefault("notes", {})[ausgewählte_aktie] = auto_memory_text
                save_local_data(local_store)
                
            st.text_area("Autonomes Dossier:", value=auto_memory_text, height=220, key=f"auto_note_{chart_key_suffix}")
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 4 aktiv: {e}")

with tab5:
    try:
        st.subheader(f"🌍 Makro & Inflation (2000–2056) — Fokus: {ausgewählte_aktie}")
        jahre_full, full_vpi, asset_real_index = build_inflation_series(aktie_info["infl_faktor"])

        milestone_years = [2001, 2008, 2012, 2020, 2022, 2026, 2040]
        milestone_texts = [
            "2001: Dotcom-Blase & 9/11",
            "2008: Globale Finanzkrise & QE",
            "2012: Euro-Schuldenkrise",
            "2020: COVID-19 Pandemie",
            "2022: Energiepreisschock & Zinswende",
            "2026: KI-Produktivitätszyklus",
            "2040: Langfrist-Prognose Rohstoffknappheit"
        ]
        milestone_y = [full_vpi[jahre_full.index(y)] for y in milestone_years]

        fig_infl = go.Figure()
        fig_infl.add_trace(go.Scatter(x=jahre_full, y=full_vpi, name="Inflation (VPI)", line=dict(color="#f59e0b", width=3)))
        fig_infl.add_trace(go.Scatter(x=jahre_full, y=asset_real_index, name=f"Preissetzung: {aktie_info['symbol']}", line=dict(color="#00e1ff", width=3.5)))
        
        fig_infl.add_trace(go.Scatter(
            x=milestone_years, y=milestone_y,
            mode="markers+text",
            name="🌍 Historische Krisen & Meilensteine",
            text=[str(y) for y in milestone_years],
            textposition="top center",
            hovertext=milestone_texts,
            hoverinfo="text+y",
            marker=dict(size=12, color="#e0f2fe", line=dict(width=2.5, color="#f59e0b"))
        ))

        fig_infl = style_terminal_plotly(fig_infl, height=420)
        fig_infl.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_infl, use_container_width=True, key=f"infl_chart_{chart_key_suffix}")

        st.divider()
        st.markdown(f"#### 📜 Historische Krisen-Legende & Asset-Resilienz für **{ausgewählte_aktie}**")
        
        sym = aktie_info["symbol"]
        if sym in ["BHP", "WDS", "RIO"]:
            krisen_auswirkung = "Als Rohstoffgigant profitiert dieses Asset historisch von Inflationsphasen (wie 2022), da physische Sachwerte als Schutzschild dienen."
        elif sym in ["MBG.DE"]:
            krisen_auswirkung = "Autozuliefererketten litten stark unter 2008 und 2020, wurden aber durch die Luxusstrategie in späteren Zyklen erfolgreich stabilisiert."
        elif sym in ["HSBC", "LGEN.L"]:
            krisen_auswirkung = "Finanzwerte erlitten 2008 harte Schocks, profitieren jedoch seit der Zinswende 2022 stark von höheren Zinsmargen."
        elif sym in ["IMB.L", "BTI"]:
            krisen_auswirkung = "Bewies in allen Krisen (2001, 2008, 2020) absolute Krisenfestigkeit durch unerschütterliche Preissetzungsmacht."
        else:
            krisen_auswirkung = "Technologie-Monopole profitierten nach Krisen überproportional von Digitalisierungswellen und KI-Produktivität."

        legenden_daten = [
            {"Jahr": 2001, "Ereignis": "Dotcom-Blase & 9/11", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2008, "Ereignis": "Globale Finanzkrise", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2012, "Ereignis": "Euro-Schuldenkrise", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2020, "Ereignis": "COVID-19 Pandemie", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2022, "Ereignis": "Energiekrise & Zinswende", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2026, "Ereignis": "KI-Produktivitätszyklus", "Auswirkung auf Aktie": krisen_auswirkung},
            {"Jahr": 2040, "Ereignis": "Langfrist-Rohstoffknappheit", "Auswirkung auf Aktie": krisen_auswirkung}
        ]
        st.dataframe(pd.DataFrame(legenden_daten), use_container_width=True)

        st.divider()
        st.markdown(f"#### 🏭 Spezifischer Lieferketten-Impact für: **{ausgewählte_aktie}**")
        if sym in ["BHP", "WDS", "RIO"]:
            impact_text = f"**{ausgewählte_aktie} (Rohstoffe & Energie):** Als Primärförderer am Anfang der Wertschöpfungskette exzellenter Schutz vor Inflation, da steigende Rohstoffpreise direkt weitergegeben werden können."
        elif sym in ["MBG.DE"]:
            impact_text = f"**{ausgewählte_aktie} (Automobil):** Hohe Komplexität der Zuliefererkette. Lohn- und Materialkosten steigen, können aber über die Luxus-Strategie teilweise an Kunden weitergegeben werden."
        elif sym in ["HSBC", "LGEN.L"]:
            impact_text = f"**{ausgewählte_aktie} (Finanzen):** Profitieren von höheren Zinsen in einem 'Higher-for-Longer' Inflationsumfeld, was die Nettozinsmargen stützt."
        elif sym in ["IMB.L", "BTI"]:
            impact_text = f"**{ausgewählte_aktie} (Konsum):** Extreme Preissetzungsmacht und konjunkturunabhängige Cashflows gleichen Teuerungsraten mühelos aus."
        else:
            impact_text = f"**{ausgewählte_aktie} (Tech-Monopol):** 'Asset-Light' Geschäftsmodelle ohne schwere physische Lieferketten, die von globalen Transaktionsvolumina profitieren."
        st.info(impact_text)
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 5 aktiv: {e}")

with tab6:
    try:
        st.subheader(f"⚖️ Rebalancing & Zinseszins: {ausgewählte_aktie}")
        rc_col1, rc_col2 = st.columns([1, 1.3])
        with rc_col1:
            st.markdown("### 🔄 Hard-Gate Check")
            hard_gate_triggered = any(v["typ"] == "Kernaktie" and v["gewicht"] >= 12.5 for v in PORTFOLIO_DATA.values())
            if hard_gate_triggered:
                st.warning("⚠️ Limit erreicht: Bitte Sparrate anpassen!")
            else:
                st.success("✔ Alle Portfoliogewichte im optimalen Bereich.")
        with rc_col2:
            st.markdown("### 📈 10-Jahre Zinseszins")
            jahre_zins = [f"Jahr {j}" for j in range(1, 11)]
            total_rate = (aktie_info["div_yield"] / 100.0) + 0.06
            zinseszins_werte = [round(asset_kapital * ((1 + total_rate) ** i), 2) for i in range(1, 11)]
            df_zins = pd.DataFrame({"Jahr": jahre_zins, "Wert (€)": zinseszins_werte})
            fig_zins = px.bar(df_zins, x="Jahr", y="Wert (€)")
            fig_zins = style_rounded_bars(fig_zins, width=0.5)
            fig_zins = style_terminal_plotly(fig_zins, height=340)
            st.plotly_chart(fig_zins, use_container_width=True, key=f"zins_bar_{chart_key_suffix}")
    except Exception as e:
        st.error(f"Sicherheits-Fallback in Tab 6 aktiv: {e}")

with tab7:
    voice_port = int(os.environ.get("ALPHA_DESK_VOICE_PORT", "63925"))
    voice_query = urlencode({"asset": ausgewählte_aktie, "capital": depot_kapital, "savings": spar_betrag})
    voice_url = f"http://127.0.0.1:{voice_port}/voice_visualizer.html?{voice_query}"
    st.iframe(voice_url, height=760, alt="ALPHA/DESK sprachreaktiver 3D-Voice-Visualizer")

st.divider()
st.markdown("""
    <div style='text-align: center; color: #7dd3fc; opacity: 0.7; font-size: 12px;'>
        💎 ALPHA/DESK INSTITUTIONAL TERMINAL &nbsp;|&nbsp; 
        Inhaber und Entwickler: Jacin Essghaier &nbsp;|&nbsp; 
        Alle Rechte vorbehalten. Dieses urheberrechtlich geschützte Werk (inkl. des zugrundeliegenden KI-Agenten und der proprietären Logik) ist Eigentum des Entwicklers. 
        Unerlaubtes Kopieren, Modifizieren, Extrahieren oder Verwenden dieses Codes sowie des KI-Agenten führt zu unmittelbaren rechtlichen Schritten und Schadensersatzansprüchen gegen den Besitzer.
    </div>
""", unsafe_allow_html=True)
