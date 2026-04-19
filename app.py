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
    
    # Gestione Accesso
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pw = st.text_input("Password", type="password")
        if pw == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.stop()
    
    # NAVIGAZIONE
    st.subheader("📍 Menu")
    menu = st.radio("Seleziona sezione:", ["🏠 Home", "📇 Anagrafica", "🏗️ Scheda Lavori"])
    
    st.divider()
    if st.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# 3. TESTATA A DESTRA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- 5. LOGICA DELLE PAGINE ---

if menu == "🏠 Home":
    st.title("Benvenuta, Silvia")
    st.write("Suite gestionale attiva. Seleziona una voce dal menu a sinistra per iniziare.")

elif menu == "📇 Anagrafica":
    st.header("📇 Gestione Anagrafica")

    # CERCA IN ALTO
    search = st.text_input("🔍 Cerca cliente (nome, cognome o lettera):")
    
    # FILTRO DATI
    if search:
        df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    else:
        df_filtered = df

    # TASTO AGGIUNGI SOPRA
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        with st.expander("Compila i dati del nuovo cliente", expanded=True):
            with st.form("nuovo_profilo"):
                nuovi_input = {}
                for col in df.columns:
                    nuovi_input[col] = st.text_input(f"{col}")
                if st.form_submit_button("SALVA IN ANAGRAFICA"):
                    new_df = pd.concat([df, pd.DataFrame([nuovi_input])], ignore_index=True)
                    conn.update(data=new_df)
                    st.success("Nuovo cliente registrato!")
                    st.rerun()

    st.write("---")
    
    # TABELLA EDITABILE
    st.write("Modifica i dati direttamente nella tabella qui sotto:")
    edited_df = st.data_editor(df_filtered, num_rows="dynamic", use_container_width=True, key="edit_anagrafica")

    # TASTI AGGIORNA/CANCELLA SOTTO
    col_a, col_b = st.columns([1, 4])
    if col_a.button("🔄 AGGIORNA TUTTO"):
        # Se stiamo visualizzando i dati filtrati, dobbiamo ricomporre il dataframe totale prima di salvare
        if search:
            df.update(edited_df)
            conn.update(data=df)
        else:
            conn.update(data=edited_df)
        st.success("Sincronizzazione completata!")
        st.cache_data.clear()

elif menu == "🏗️ Scheda Lavori":
    st.header("🏗️ Scheda Lavori")
    st.write("Visualizzazione avanzamento cantieri:")
    st.dataframe(df, use_container_width=True)
