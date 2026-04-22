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

# --- STILE CSS CATTIVO E LEGGIBILE ---
st.markdown("""
    <style>
    /* SIDEBAR */
    section[data-testid="stSidebar"] button div p {
        font-size: 18px !important; 
        font-weight: 900 !important;
        text-transform: uppercase;
    }
    
    /* CARD DASHBOARD - CORTE MA LARGHE */
    .card-home {
        background-color: white;
        padding: 4px 10px;
        border-radius: 8px;
        border: 3px solid #1e293b;
        height: 95px; 
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    /* TITOLI CARD - GIGANTI */
    .card-home h3 {
        font-size: 1.4rem !important;
        font-weight: 950;
        border-bottom: 4px solid #1e293b;
        margin-bottom: 5px;
        text-transform: uppercase;
        color: #000;
    }

    /* NOMI CLIENTI - ENORMI */
    .client-name { 
        font-weight: 950; 
        font-size: 22px !important; 
        color: #000; 
    }
    
    .item-row {
        padding: 2px 0;
        border-bottom: 1px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* DATE E PRATICHE - LEGGIBILI */
    .date-badge { 
        padding: 4px 12px; 
        border-radius: 6px; 
        font-size: 18px !important; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: white; 
        min-width: 100px;
        text-align: center;
    }
    
    .pratica-txt {
        font-size: 16px !important;
        font-weight: 800;
        color: #1e293b;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 950; 
        font-size: 22px !important;
    }

    /* SCROLLBAR */
    .card-home::-webkit-scrollbar { width: 5px; }
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

# --- DATI ---
df = pd.read_sql("SELECT * FROM lavori", conn)

# --- LOGICA ---
if st.session_state.menu == "HOME":
    st.markdown("<h2 style='font-weight:950; margin-bottom:15px;'>STUDIO DASHBOARD</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card-home"><h3>🚦 SCADENZE</h3>', unsafe_allow_html=True)
        q = df[(df['Scadenza'] != "") & (df['Stato'] != "Conclusa")].sort_values(by="Scadenza").head(5)
        for _, r in q.iterrows():
            st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><div class="date-badge">{r["Scadenza"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card-home"><h3>🏗️ LAVORI</h3>', unsafe_allow_html=True)
        for _, r in df.tail(5).iloc[::-1].iterrows():
            st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span class="pratica-txt">{r["Pratica"]}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card-home"><h3>⚠️ ALERT</h3>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            miss = [k for k, v in inizializza_documenti(r['docs_json'], r['Pratica']).items() if "🔴" in v]
            if miss:
                st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span class="alert-text">{len(miss)}!!</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.menu == "ANAGRAFICA":
    mostra_anagrafica(conn)
elif st.session_state.menu == "LAVORI":
    mostra_lavori(conn)

# Riga 150
# Riga 151
# Riga 152
# Riga 153
# Riga 154
# Riga 155
# Riga 156
# Riga 157
# Fine_Codice_Archiflow
