import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import inizializza_documenti

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Archiflow - Arch. Cubeddu", layout="wide")

# --- CONNESSIONE SUPABASE (Integrazione Segreta) ---
@st.cache_resource
def init_supabase():
    # Recupero dati dai secrets che hai incollato su Streamlit
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    section[data-testid="stSidebar"] button div p {
        font-size: 18px !important; 
        font-weight: 900 !important;
        text-transform: uppercase;
    }
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
    .alert-text {
        color: #ef4444; 
        font-weight: 950; 
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DI ACCESSO ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.sidebar.title("🔐 Login")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Accedi"):
        if pwd == st.secrets["supabase"]["password"]:
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.sidebar.error("Password errata")
    st.warning("Inserisci la password per accedere al gestionale.")
    st.stop()

# --- NAVIGAZIONE ---
if "menu" not in st.session_state:
    st.session_state.menu = "HOME"

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏛️ ARCHIFLOW</h2>", unsafe_allow_html=True)
    st.write(f"Utente: Arch. Silvia Cubeddu")
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
    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()

# --- CARICAMENTO DATI DA SUPABASE ---
@st.cache_data(ttl=60)
def load_data():
    # Legge la tabella 'lavori' da Supabase
    res = supabase.table("lavori").select("*").execute()
    return pd.DataFrame(res.data)

try:
    df = load_data()
except Exception as e:
    st.error(f"Errore caricamento dati: {e}")
    df = pd.DataFrame()

# --- LOGICA PAGINE ---
if st.session_state.menu == "HOME":
    st.markdown("<h1 style='font-weight:950; margin-bottom:15px;'>Archiflow - Suite Gestionale</h1>", unsafe_allow_html=True)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="card-home"><h3>🚦 SCADENZE</h3>', unsafe_allow_html=True)
            # Filtro scadenze (assicurati che la colonna si chiami 'Scadenza')
            if 'Scadenza' in df.columns:
                q = df[(df['Scadenza'].fillna("") != "") & (df['Stato'] != "Conclusa")].sort_values(by="Scadenza").head(5)
                for _, r in q.iterrows():
                    st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><div class="date-badge">{r["Scadenza"]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card-home"><h3>🏗️ LAVORI</h3>', unsafe_allow_html=True)
            for _, r in df.tail(5).iloc[::-1].iterrows():
                st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span style="font-weight:bold;">{r.get("Pratica", "")}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="card-home"><h3>⚠️ ALERT DOCS</h3>', unsafe_allow_html=True)
            for _, r in df.iterrows():
                docs = r.get('docs_json', '{}')
                miss = [k for k, v in inizializza_documenti(docs, r.get('Pratica', '')).items() if "🔴" in v]
                if miss:
                    st.markdown(f'<div class="item-row"><span class="client-name">{r["Cliente"]}</span><span class="alert-text">{len(miss)}!!</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Benvenuta! Inizia aggiungendo dei dati nella sezione Anagrafica o Lavori.")

elif st.session_state.menu == "ANAGRAFICA":
    # Passiamo il client supabase invece della connessione sqlite
    mostra_anagrafica(supabase)

elif st.session_state.menu == "LAVORI":
    # Passiamo il client supabase invece della connessione sqlite
    mostra_lavori(supabase)
