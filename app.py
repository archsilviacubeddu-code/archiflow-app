import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS Custom per mantenere la tua estetica ed eliminare bordi inutili
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* MENU SIDEBAR */
    .sidebar-btn > div > button {
        height: 4.5em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* CARDS HOME - Pulite e professionali */
    .card-home {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        min-height: 400px;
        margin-bottom: 20px;
    }
    
    /* Titoli sezioni Home */
    .card-home h3 {
        color: #1e293b;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURAZIONE DATABASE UNIFICATO
DB_FILE = "database_archiflow.csv"
# Abbiamo aggiunto 'docs_json' per i semafori dei documenti
COLONNE = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note", "docs_json"]

def carica_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str).fillna("")
        for c in COLONNE:
            if c not in df.columns: df[c] = ""
        return df[COLONNE]
    return pd.DataFrame(columns=COLONNE)

# 3. NAVIGAZIONE SIDEBAR CON LOGO
if "menu_sel" not in st.session_state: 
    st.session_state.menu_sel = "HOME"

with st.sidebar:
    # --- GESTIONE LOGO O TITOLO ---
    if os.path.exists("Logo.png"):
        # Se c'è il file Logo.png, mostralo
        st.image("Logo.png", use_container_width=True)
    else:
        # Altrimenti, metti un titolo testuale pulito
        st.markdown("<h1 style='text-align: center; color: #1e293b;'>🏛️ ARCHIFLOW</h1>", unsafe_allow_html=True)
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
        # Reset delle selezioni dei lavori per non avere vecchi dati caricati
        st.session_state.sezione_lavoro = None
        st.session_state.lavoro_sel = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4. CARICAMENTO DATI GLOBALE (Unico Cervello)
df_globale = carica_db()

# 5. LOGICA PAGINE
menu = st.session_state.menu_sel

if menu == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.write("Quadro generale delle attività.")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1: # SEMAFORO SCADENZE
        st.markdown('<div class="card-home"><h3>🚦 Scadenze Lavori</h3>', unsafe_allow_html=True)
        # Filtriamo solo i lavori con una scadenza e non chiusi
        if not df_globale.empty:
            df_scadenze = df_globale[(df_globale['Scadenza'] != "") & (df_globale['Stato'] != "Chiusa")]
            if not df_scadenze.empty:
                # Mostriamo solo le colonne essenziali ordinando per scadenza
                st.dataframe(df_scadenze[["Cliente", "Pratica", "Scadenza"]].sort_values(by="Scadenza"), use_container_width=True, hide_index=True)
            else:
                st.info("Nessuna scadenza imminente.")
        else:
            st.write("Database vuoto.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2: # NUOVI LAVORI
        st.markdown('<div class="card-home"><h3>🆕 Ultimi Inserimenti</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            # Mostriamo gli ultimi 5 inserimenti
            st.dataframe(df_globale[["Cliente", "Pratica"]].tail(5), use_container_width=True, hide_index=True)
        else:
            st.write("Database vuoto.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3: # ALERT DOCUMENTI
        st.markdown('<div class="card-home"><h3>⚠️ Alert Documenti</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            # Usiamo la funzione del tuo file gestione_documenti.py
            widget_alert_home(df_globale)
        else:
            st.write("Database vuoto.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "ANAGRAFICA":
    # Passiamo il database globale, il file e lo schema colonne
    mostra_anagrafica(df_globale, DB_FILE, COLONNE)

elif menu == "LAVORI":
    # Passiamo il database globale e il file
    mostra_lavori(df_globale, DB_FILE)
