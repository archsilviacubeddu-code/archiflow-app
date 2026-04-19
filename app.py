import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS per allineare il titolo a destra e gestire il logo
st.markdown("""
    <style>
    .titolo-destra {
        text-align: right;
        font-family: 'Helvetica';
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# Intestazione: Logo a sinistra e Titolo a destra
col1, col2 = st.columns([1, 2])
with col1:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("*(Carica logo.png su GitHub)*")

with col2:
    st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: right;">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)

# Password di accesso
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    pw = st.text_input("Inserisci Password", type="password")
    if pw == st.secrets["password"]:
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.stop()

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0") # ttl=0 forza l'aggiornamento immediato

# --- SEZIONE ANAGRAFICA (EDITABILE) ---
st.header("📇 Anagrafica e Gestione Cantieri")

# Editor dei dati: permette di modificare, aggiungere e cancellare righe
edited_df = st.data_editor(
    df, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="editor_anagrafica"
)

# Pulsante per salvare le modifiche su Google Sheet
if st.button("Aggiorna Google Sheet"):
    try:
        conn.update(data=edited_df)
        st.success("Dati aggiornati correttamente su Google Sheet!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Errore durante l'aggiornamento: {e}")

st.info("💡 Puoi modificare le celle, aggiungere righe in fondo o selezionare una riga e premere 'Canc' per eliminarla. Ricorda di cliccare 'Aggiorna' dopo ogni modifica.")
