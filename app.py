import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
import json

# IMPORTA LE TUE FUNZIONI DAI FILE ESTERNI
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import inizializza_documenti

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Archiflow", layout="wide")

# --- CONNESSIONE DATABASE (OTTIMIZZATA PER CLOUD) ---
@st.cache_resource
def get_engine():
    try:
        # Recupero URL dai Secrets
        db_url = st.secrets["database"]["url"]
        # Creiamo un engine con pool di connessioni per evitare "Too many connections"
        return create_engine(db_url, pool_size=5, max_overflow=10)
    except Exception as e:
        st.error(f"Errore di configurazione: {e}")
        st.stop()

engine = get_engine()

# --- STILE CSS (INTEGRALE) ---
st.markdown("""
    <style>
    /* SIDEBAR */
    section[data-testid="stSidebar"] button div p {
        font-size: 18px !important; 
        font-weight: 900 !important;
        text-transform: uppercase;
    }
    
    /* CARD DASHBOARD */
    .card-home {
        background-color: white;
        padding: 4px 10px;
        border-radius: 8px;
        border: 3px solid #1e293b;
        height: 120px; 
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    .card-home h3 {
        font-size: 1.4rem !important;
        font-weight: 950;
        border-bottom: 4px solid #1e293b;
        margin-bottom: 5px;
        text-transform: uppercase;
        color: #000;
    }

    .client-name { 
        font-weight: 950; 
        font-size: 20px !important; 
        color: #000; 
    }
    
    .item-row {
        padding: 4px 0;
        border-bottom: 1px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .date-badge { 
        padding: 4px 12px; 
        border-radius: 6px; 
        font-size: 16px !important; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: white; 
    }
    
    .pratica-txt {
        font-size: 16px !important;
        font-weight: 800;
        color: #1e293b;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 950; 
        font-size: 20px !important;
    }
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

# --- CARICAMENTO DATI (SICURO) ---
try:
    with engine.connect() as connection:
        df = pd.read_sql(text("SELECT * FROM lavori"), connection)
except Exception as e:
    st.error(f"Errore di lettura dal Database: {e}")
    st.info("Verifica che la tabella 'lavori' esista su Supabase.")
    st.stop()

# --- LOGICA PAGINE ---
if st.session_state.menu == "HOME":
    st.markdown("<h1 style='font-weight:950; margin-bottom:15px;'>Archiflow - Suite Gestionale</h1>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Nessun dato presente. Vai in Anagrafica per aggiungere il primo lavoro.")
    else:
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown('<div class="card-home"><h3>🚦 SCADENZE</h3>', unsafe_allow_html=True)
            # Filtro scadenze attive (pulizia valori nulli/vuoti)
            scad = df[(df['Scadenza'].get_notnull() if hasattr(df['Scadenza'], 'get_notnull') else df['Scadenza'] != "") & (df['Stato'] != "Conclusa")]
            if not scad.empty:
                scad = scad.sort_values(by="Scadenza").head(5)
                for _, r in scad.iterrows():
                    st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><div class="date-badge">{r["Scadenza"]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="card-home"><h3>🏗️ LAVORI RECENTI</h3>', unsafe_allow_html=True)
            for _, r in df.tail(5).iloc[::-1].iterrows():
                st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span class="pratica-txt">{r["Pratica"]}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c3:
            st.markdown('<div class="card-home"><h3>⚠️ ALERT DOCS</h3>', unsafe_allow_html=True)
            for _, r in df.iterrows():
                # Inizializza documenti (gestendo il JSON dal DB)
                docs_dict = inizializza_documenti(r['docs_json'], r['Pratica'])
                miss = [k for k, v in docs_dict.items() if "🔴" in v]
                if miss:
                    st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span class="alert-text">{len(miss)} 🔴</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Per le pagine esterne, apriamo una connessione dedicata
elif st.session_state.menu == "ANAGRAFICA":
    with engine.connect() as conn:
        mostra_anagrafica(conn)

elif st.session_state.menu == "LAVORI":
    with engine.connect() as conn:
        mostra_lavori(conn)
