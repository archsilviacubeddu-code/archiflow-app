import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Archiflow Suite", layout="wide")

# CSS per il titolo a destra
st.markdown("""
    <style>
    .titolo-destra { text-align: right; color: #333333; font-family: 'Helvetica'; margin-bottom: 0; }
    .sottotitolo-destra { text-align: right; color: #666666; font-size: 1.1rem; margin-top: 0; }
    div.stButton > button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU LATERALE (Con il Logo!)
with st.sidebar:
    try:
        # Cerchiamo di caricare il logo
        st.image("Logo.png", use_container_width=True)
    except:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.info("🖼️ Carica il file 'Logo.png' su GitHub per vederlo qui.")
    
    st.divider()
    st.subheader("📍 Navigazione")
    menu = st.radio("Vai a:", ["🏠 Home", "📇 Anagrafica", "🏗️ Scheda Lavori"])
    
    st.divider()
    if st.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# 3. TESTATA FISSA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Inizializziamo lo stato se non esiste
if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = None

# --- LOGICA DELLE PAGINE ---

if menu == "🏠 Home":
    st.title("Benvenuta, Silvia 🏛️")
    st.write("Suite operativa. Gestisci i tuoi cantieri in modo semplice e veloce.")

elif menu == "📇 Anagrafica":
    st.header("📇 Gestione Anagrafica")
    
    # Ricerca automatica
    cerca = st.text_input("🔍 Cerca cliente (Nome o Cognome):")
    
    # Se cerchi, filtriamo i dati
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    # TABELLA TUTTA EDITABILE (come hai chiesto)
    st.write("Modifica direttamente i dati qui sotto. Il salvataggio avviene alla pressione del tasto.")
    edited_df = st.data_editor(df_filtered, num_rows="dynamic", use_container_width=True, key="editor_anagrafica")
    
    # SALVATAGGIO AUTOMATICO SIMULATO (con tasto rapido sotto)
    if st.button("💾 SALVA MODIFICHE"):
        conn.update(data=edited_df)
        st.success("Dati sincronizzati con Google Sheets! ✅")
        st.cache_data.clear()

elif menu == "🏗️ Scheda Lavori":
    st.header("🏗️ Scheda Lavori")
    
    # PULSANTIERA CATEGORIE
    st.write("### Seleziona Categoria:")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    tipo_lavoro = None
    if col1.button("🏗️ Direzione Lavori"): tipo_lavoro = "Direzione Lavori"
    if col2.button("📋 Pratiche"): tipo_lavoro = "Pratiche"
    if col3.button("📏 Rilievi"): tipo_lavoro = "Rilievi"
    if col4.button("📊 Millesimi"): tipo_lavoro = "Millesimi"
    if col5.button("➕ Altro"): tipo_lavoro = "Altro"
    
    if tipo_lavoro:
        st.subheader(f"Dettaglio: {tipo_lavoro}")
        # Qui filtriamo la tabella per farti vedere solo quei lavori
        if 'Pratica' in df.columns:
            df_lavoro = df[df['Pratica'] == tipo_lavoro]
            st.dataframe(df_lavoro, use_container_width=True)
        else:
            st.warning(f"Assicurati che nel tuo file Excel ci sia una colonna chiamata 'Pratica'.")
