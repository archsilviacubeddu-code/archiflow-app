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
    
    st.subheader("📍 Menu")
    menu = st.radio("Vai a:", ["🏠 Home", "📇 Anagrafica", "🏗️ Scheda Lavori"])

# 3. TESTATA A DESTRA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- LOGICA PAGINA ANAGRAFICA ---
if menu == "📇 Anagrafica":
    st.header("📇 Gestione Totale Anagrafica")

    # CERCA IN ALTO
    search = st.text_input("🔍 Cerca nel database (scrivi nome, cognome o lettera):")
    
    # FILTRO
    if search:
        df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    else:
        df_filtered = df

    st.write("### 📝 Tabella Editabile")
    st.info("Clicca su qualsiasi cella per modificare. Puoi aggiungere righe in fondo o cancellarle selezionandole.")
    
    # LA TABELLA DOVE TUTTO È EDITABILE
    # num_rows="dynamic" permette di aggiungere/togliere righe liberamente
    edited_df = st.data_editor(
        df_filtered, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="editor_universale"
    )

    st.divider()

    # TASTO SALVATAGGIO SEMPRE PRESENTE
    if st.button("💾 AGGIORNA E SALVA TUTTO SU GOOGLE SHEETS"):
        try:
            # Se hai filtrato, dobbiamo riportare le modifiche nel dataframe originale
            if search:
                df.update(edited_df)
                conn.update(data=df)
            else:
                conn.update(data=edited_df)
            
            st.success("✅ Tutto salvato correttamente!")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Errore durante il salvataggio: {e}")

elif menu == "🏠 Home":
    st.title("Benvenuta Silvia")
    st.write("Seleziona 'Anagrafica' per modificare i dati.")

elif menu == "🏗️ Scheda Lavori":
    st.header("🏗️ Visualizzazione Lavori")
    st.dataframe(df, use_container_width=True)
