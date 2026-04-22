import streamlit as st
import pandas as pd
import sqlite3
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import inizializza_documenti

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Archiflow", layout="wide")

# --- DATABASE ---
conn = sqlite3.connect("archiflow_db.sqlite", check_same_thread=False)
conn.execute('''
    CREATE TABLE IF NOT EXISTS lavori (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        Cliente TEXT, CF_PIVA TEXT, Indirizzo TEXT, CAP TEXT, 
        Citta TEXT, Telefono TEXT, Email TEXT, Web TEXT, 
        Pratica TEXT, Stato TEXT, Scadenza TEXT, Note TEXT, docs_json TEXT
    )
''')

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    /* SIDEBAR */
    section[data-testid="stSidebar"] button div p {
        font-size: 18px !important; 
        font-weight: 900 !important;
        color: #1e293b !important;
        text-transform: uppercase;
    }
    
    /* CARD DASHBOARD - CORTE (80px) */
    .card-home {
        background-color: white;
        padding: 4px 10px;
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        height: 80px; 
        overflow-y: auto;
        margin-bottom: 8px;
    }
    
    /* TITOLI CARD - MOLTO GROSSI */
    .card-home h3 {
        font-size: 1.3rem !important;
        font-weight: 900;
        border-bottom: 3px solid #1e293b;
        padding-bottom: 0px;
        margin-bottom: 4px;
        text-transform: uppercase;
        color: #000;
    }

    /* CONTENUTI RIGHE */
    .client-name { 
        font-weight: 900; 
        font-size: 16px !important; 
        color: #000; 
    }
    
    .item-row {
        padding: 1px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* BADGE E ALERT */
    .date-badge { 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-size: 12px !important; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: white; 
        min-width: 80px;
        text-align: center;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 900; 
        font-size: 16px !important;
    }

    /* SCROLLBAR */
    .card-home::-webkit-scrollbar { width: 3px; }
    .card-home::-webkit-scrollbar-thumb { background: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# --- NAVIGAZIONE ---
if "menu" not in st.session_state:
    st.session_state.menu = "HOME"

with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align:center;'>🏛️ ARCHIFLOW</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.menu = "HOME"
        st.rerun()
        
    if st.button("📇 ANAGRAFICA", use_container_width=True):
        st.session_state.menu = "ANAGRAFICA"
        st.rerun()
        
    if st.button("🏗️ LAVORI", use_container_width=True):
        st.session_state.menu = "LAVORI"
        st.rerun()

# --- CARICAMENTO DATI ---
df = pd.read_sql("SELECT * FROM lavori", conn)

# --- LOGICA PAGINE ---
if st.session_state.menu == "HOME":
    st.markdown("<h2 style='font-weight:900; margin-bottom:10px;'>Dashboard Studio</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        q_scad = df[(df['Scadenza'] != "") & (df['Stato'] != "Conclusa")].sort_values(by="Scadenza").head(5)
        for _, r in q_scad.iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <div class="date-badge">{r["Scadenza"]}</div>
                </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🏗️ Lavori</h3>', unsafe_allow_html=True)
        for _, r in df.tail(5).iloc[::-1].iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <span style="font-size:12px; font-weight:800;">{r["Pratica"]}</span>
                </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-home"><h3>⚠️ Alert</h3>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            docs = inizializza_documenti(r['docs_json'], r['Pratica'])
            miss = [k for k, v in docs.items() if "🔴" in v]
            if miss:
                st.markdown(f'''
                    <div class="item-row">
                        <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                        <span class="alert-text">{len(miss)}!!</span>
                    </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "ANAGRAFICA":
    mostra_anagrafica(conn)

elif st.session_state.menu == "LAVORI":
    mostra_lavori(conn)

# Linea 156
# Linea 157
# Fine Codice
