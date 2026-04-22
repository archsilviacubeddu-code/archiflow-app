import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home, inizializza_documenti

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# --- DATABASE ENGINE (Sempre attivo per PC e Telefono) ---
DB_NAME = "archiflow_db.sqlite"
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

conn = get_connection()
conn.execute('''
    CREATE TABLE IF NOT EXISTS lavori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Cliente TEXT, CF_PIVA TEXT, Indirizzo TEXT, CAP TEXT, 
        Citta TEXT, Telefono TEXT, Email TEXT, Web TEXT, 
        Pratica TEXT, Stato TEXT, Scadenza TEXT, Note TEXT, docs_json TEXT
    )
''')
conn.commit()

# --- CSS DEFINITIVO: BOTTONI SIDEBAR GROSSI E CARD HOME PICCOLE ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* TITOLO SIDEBAR */
    .sidebar-title {
        font-size: 24px !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 20px;
        color: #1e293b;
    }

    /* BOTTONI SIDEBAR: GROSSI, QUADRATI E UGUALI */
    div.stButton > button {
        height: 120px !important; /* Altezza fissa per farli quadrati/grossi */
        width: 100% !important;
        margin-bottom: 15px !important;
        border-radius: 15px !important;
        border: 3px solid #1e293b !important;
        background-color: white !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* TESTO BOTTONI: GRASSETTO TOTALE */
    div.stButton > button p {
        font-weight: 900 !important;
        font-size: 18px !important;
        color: #1e293b !important;
        text-transform: uppercase;
        margin: 0 !important;
    }

    div.stButton > button:hover {
        background-color: #f1f5f9 !important;
    }

    /* CARD HOME: TORNATE PICCOLE E COMPATTE */
    .card-home {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        height: 320px; /* Altezza ridotta */
        overflow-y: auto;
    }
    
    .card-home h3 {
        color: #0f172a;
        font-size: 1.2rem !important;
        font-weight: 900;
        margin-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 5px;
    }

    .item-row {
        padding: 8px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .client-name { font-weight: 800; color: #1e293b; font-size: 15px !important; }
    .pratica-type { color: #64748b; font-size: 10px; text-transform: uppercase; font-weight: 700; }
    .date-badge { padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 900; background-color: #1e293b; color: white; }
    .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .bg-red { background-color: #ef4444; }
    .bg-yellow { background-color: #f59e0b; }
    .bg-green { background-color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGAZIONE ---
if "menu_sel" not in st.session_state: 
    st.session_state.menu_sel = "HOME"

with st.sidebar:
    st.markdown('<div class="sidebar-title">🏛️ ARCHIFLOW</div>', unsafe_allow_html=True)
    st.divider()
    
    if st.button("🏠 HOME"): 
        st.session_state.menu_sel = "HOME"
        st.rerun()
    if st.button("📇 ANAGRAFICA"): 
        st.session_state.menu_sel = "ANAGRAFICA"
        st.rerun()
    if st.button("🏗️ LAVORI"): 
        st.session_state.menu_sel = "LAVORI"
        st.rerun()

# Caricamento Dati
df_globale = pd.read_sql("SELECT * FROM lavori", conn)

# --- LOGICA PAGINE ---
if st.session_state.menu_sel == "HOME":
    st.title("Studio Overview")
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        df_scad = df_globale[df_globale['Scadenza'] != ""].copy()
        if not df_scad.empty:
            for _, r in df_scad.sort_values(by="Scadenza").head(10).iterrows():
                st_l = r['Stato'].lower()
                dot = "bg-red"
                if "corso" in st_l: dot = "bg-yellow"
                elif "chius" in st_l: dot = "bg-green"
                st.markdown(f'''
                    <div class="item-row">
                        <div style="display:flex;align-items:center;">
                            <span class="status-dot {dot}"></span>
                            <div><span class="client-name">{r["Cliente"]}</span><br><span class="pratica-type">{r["Pratica"]}</span></div>
                        </div>
                        <div class="date-badge">{r["Scadenza"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🆕 Ultimi</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            for _, r in df_globale.tail(10).iloc[::-1].iterrows():
                if r['Cliente'].strip() != "":
                    st.markdown(f'<div class="item-row"><div><span class="client-name">{r["Cliente"]}</span><br><span class="pratica-type">{r["Pratica"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-home"><h3>⚠️ Alert</h3>', unsafe_allow_html=True)
        alert_found = False
        if not df_globale.empty:
            for _, r in df_globale.iterrows():
                docs = inizializza_documenti(r['docs_json'], r['Pratica'])
                mancanti = [k for k, v in docs.items() if "🔴" in v or "🟡" in v]
                if mancanti:
                    alert_found = True
                    st.markdown(f'<div class="item-row"><div><span class="client-name">{r["Cliente"]}</span><br><span class="pratica-type" style="color:#ef4444;">{len(mancanti)} Da fare</span></div></div>', unsafe_allow_html=True)
        if not alert_found: st.success("OK")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    mostra_anagrafica(conn)
elif st.session_state.menu_sel == "LAVORI":
    mostra_lavori(conn)
