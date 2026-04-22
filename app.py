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

# --- DATABASE ENGINE (Sostituisce il CSV per l'uso PC + Telefono) ---
DB_NAME = "archiflow_db.sqlite"

def get_connection():
    # Crea il file database se non esiste nella cartella
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

# Inizializzazione Tabella (eseguita al primo avvio)
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

# --- IL TUO CSS PULITO ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* TESTO BOTTONI SIDEBAR */
    section[data-testid="stSidebar"] button div p,
    section[data-testid="stSidebar"] button span {
        font-weight: 900 !important;
        font-size: 20px !important;
        color: #1e293b !important;
    }

    /* BOTTONI SIDEBAR */
    .sidebar-btn > div > button {
        height: 4.5em !important;
        margin-bottom: 10px !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: white !important;
        transition: background 0.2s !important;
    }
    
    .sidebar-btn > div > button:hover {
        background-color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
    }

    /* CARD HOME */
    .card-home {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        min-height: 400px;
    }
    
    .card-home h3 {
        color: #0f172a;
        font-size: 1.6rem !important;
        font-weight: 800;
        margin-bottom: 20px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 10px;
    }

    .item-row {
        padding: 15px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .client-name { font-weight: 800; color: #1e293b; font-size: 18px !important; }
    .pratica-type { color: #64748b; font-size: 12px; text-transform: uppercase; font-weight: 600; margin-left: 10px; }
    .date-badge { padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 800; background-color: #1e293b; color: white; }
    .status-dot { height: 14px; width: 14px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .bg-red { background-color: #ef4444; }
    .bg-yellow { background-color: #f59e0b; }
    .bg-green { background-color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGAZIONE SIDEBAR ---
if "menu_sel" not in st.session_state: 
    st.session_state.menu_sel = "HOME"

with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🏛️ ARCHIFLOW</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): 
        st.session_state.menu_sel = "HOME"
        st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): 
        st.session_state.menu_sel = "ANAGRAFICA"
        st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): 
        st.session_state.menu_sel = "LAVORI"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Caricamento DataFrame dal Database SQL
df_globale = pd.read_sql("SELECT * FROM lavori", conn)

# --- LOGICA PAGINE ---
if st.session_state.menu_sel == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        df_scad = df_globale[df_globale['Scadenza'] != ""].copy()
        if not df_scad.empty:
            for _, r in df_scad.sort_values(by="Scadenza").head(8).iterrows():
                st_l = r['Stato'].lower()
                dot = "bg-red"
                if "corso" in st_l: dot = "bg-yellow"
                elif "chius" in st_l or "finito" in st_l: dot = "bg-green"
                st.markdown(f'''
                    <div class="item-row">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span class="status-dot {dot}"></span>
                            <div>
                                <span class="client-name">{r["Cliente"]}</span><br>
                                <span class="pratica-type">{r["Pratica"]}</span>
                            </div>
                        </div>
                        <div class="date-badge">{r["Scadenza"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
        else: st.info("Nessuna scadenza.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🆕 Ultimi Lavori</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            for _, r in df_globale.tail(8).iloc[::-1].iterrows():
                if r['Cliente'].strip() != "":
                    st.markdown(f'''
                        <div class="item-row">
                            <div>
                                <span class="client-name">{r["Cliente"]}</span><br>
                                <span class="pratica-type">{r["Pratica"]}</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-home"><h3>⚠️ Alert Necessità</h3>', unsafe_allow_html=True)
        alert_found = False
        if not df_globale.empty:
            for _, r in df_globale.iterrows():
                # Inizializza guardando il tipo pratica (CILA, SCIA, etc)
                docs = inizializza_documenti(r['docs_json'], r['Pratica'])
                mancanti = [k for k, v in docs.items() if "🔴" in v or "🟡" in v]
                if mancanti:
                    alert_found = True
                    st.markdown(f'''
                        <div class="item-row">
                            <div>
                                <span class="client-name">{r["Cliente"]}</span><br>
                                <span class="pratica-type" style="color:#ef4444;">{len(mancanti)} Azioni aperte</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
        if not alert_found: st.success("Tutto completato.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    # Passiamo l'oggetto connessione al database
    mostra_anagrafica(conn)
elif st.session_state.menu_sel == "LAVORI":
    # Passiamo l'oggetto connessione al database
    mostra_lavori(conn)
