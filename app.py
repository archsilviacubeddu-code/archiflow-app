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
            st.info("Logo non trovato")
    
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

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- 5. CERCA CLIENTE ---
st.header("🔍 Cerca Cliente")
search_term = st.text_input("Inserisci nome, cognome o una lettera per cercare:")

# Filtriamo il database in base alla ricerca
if search_term:
    mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
    results = df[mask]
else:
    results = pd.DataFrame(columns=df.columns)

# Se ci sono risultati, scegliamo quale cliente gestire
selected_index = None
if not results.empty:
    selection = st.selectbox("Seleziona il cliente esatto da gestire:", 
                             results.index, 
                             format_func=lambda x: f"{df.at[x, df.columns[0]]} - {df.at[x, df.columns[1]] if len(df.columns)>1 else ''}")
    selected_index = selection
else:
    if search_term:
        st.warning("Nessun cliente trovato con questa lettera.")

st.divider()

# --- 6. AGGIORNA, MODIFICA, CANCELLA ---
if selected_index is not None:
    st.subheader(f"Modifica dati di: {df.at[selected_index, df.columns[0]]}")
    
    with st.form("form_edit"):
        updated_values = {}
        cols = df.columns.tolist()
        
        # Creiamo i campi già popolati con i dati attuali
        for col in cols:
            updated_values[col] = st.text_input(f"{col}", value=str(df.at[selected_index, col]))
        
        c1, c2, c3 = st.columns(3)
        with c1:
            btn_modifica = st.form_submit_button("📝 MODIFICA") # Inteso come 'Applica'
        with c2:
            btn_aggiorna = st.form_submit_button("🔄 AGGIORNA SHEET")
        with c3:
            btn_cancella = st.form_submit_button("🗑️ CANCELLA")

    # Logica Azioni
    if btn_modifica or btn_aggiorna:
        for col in cols:
            df.at[selected_index, col] = updated_values[col]
        conn.update(data=df)
        st.success("Dati aggiornati correttamente!")
        st.cache_data.clear()
        st.rerun()

    if btn_cancella:
        df = df.drop(selected_index).reset_index(drop=True)
        conn.update(data=df)
        st.success("Cliente eliminato!")
        st.cache_data.clear()
        st.rerun()

# --- 7. GESTIONE ANAGRAFICA (VISUALIZZAZIONE) ---
st.divider()
st.header("📋 Gestione Anagrafica")
st.dataframe(df, use_container_width=True, hide_index=False)
