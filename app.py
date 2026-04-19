import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS per il titolo a destra
st.markdown("""
    <style>
    .titolo-destra { text-align: right; color: #333333; font-family: 'Helvetica'; margin-bottom: 0; }
    .sottotitolo-destra { text-align: right; color: #666666; font-size: 1.1rem; margin-top: 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU FISSO A SINISTRA (Sidebar)
with st.sidebar:
    try:
        st.image("Logo.png", use_container_width=True)
    except:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.info("Carica logo.png")
    
    st.divider()
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pw = st.text_input("Password", type="password")
        if pw == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.stop()
    else:
        st.success("Accesso Autorizzato")
        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.rerun()

# 3. TESTATA PRINCIPALE A DESTRA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE E CARICAMENTO DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Inizializzazione stato per il form
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# --- 5. AREA DI INSERIMENTO E MODIFICA (SOPRA) ---
st.header("🖊️ Gestione Record")

with st.container():
    # Seleziona un record per modificarlo o cancellarlo
    options = ["NUOVO RECORD"] + df.index.tolist()
    selection = st.selectbox("Seleziona ID riga da gestire (o Nuovo):", options, format_func=lambda x: f"Riga {x}" if x != "NUOVO RECORD" else x)
    
    # Form con i campi
    with st.form("form_gestione"):
        inputs = {}
        cols = df.columns.tolist()
        
        # Se abbiamo selezionato una riga, popoliamo i campi
        for col in cols:
            default_val = str(df.at[selection, col]) if selection != "NUOVO RECORD" else ""
            inputs[col] = st.text_input(f"{col}", value=default_val)
        
        # Tasti azione uno accanto all'altro
        c1, c2, c3 = st.columns(3)
        
        with c1:
            btn_add = st.form_submit_button("➕ AGGIUNGI")
        with c2:
            btn_update = st.form_submit_button("🔄 AGGIORNA")
        with c3:
            btn_delete = st.form_submit_button("🗑️ CANCELLA")

    # LOGICA DELLE AZIONI
    if btn_add:
        new_line = pd.DataFrame([inputs])
        updated_df = pd.concat([df, new_line], ignore_index=True)
        conn.update(data=updated_df)
        st.success("Aggiunto!")
        st.rerun()

    if btn_update and selection != "NUOVO RECORD":
        for col in cols:
            df.at[selection, col] = inputs[col]
        conn.update(data=df)
        st.success("Aggiornato!")
        st.rerun()

    if btn_delete and selection != "NUOVO RECORD":
        df = df.drop(selection).reset_index(drop=True)
        conn.update(data=df)
        st.success("Cancellato!")
        st.rerun()

# --- 6. VISUALIZZAZIONE (SOTTO - NON EDITABILE) ---
st.divider()
st.header("📇 Anagrafica (Sola Lettura)")
st.dataframe(df, use_container_width=True, hide_index=False)
