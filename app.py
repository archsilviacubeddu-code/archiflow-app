import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS per il titolo a destra e stile
st.markdown("""
    <style>
    .titolo-destra { text-align: right; color: #4A4A4A; font-family: 'Helvetica'; margin-bottom: 0; }
    .sottotitolo-destra { text-align: right; color: #888888; font-size: 1.2rem; margin-top: 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. Intestazione: Logo a sinistra e Titolo a destra
col_logo, col_titolo = st.columns([1, 3])
with col_logo:
    # Cerchiamo il logo sia con L maiuscola che minuscola per sicurezza
    try:
        st.image("Logo.png", width=250)
    except:
        try:
            st.image("logo.png", width=250)
        except:
            st.info("Logo non trovato")

with col_titolo:
    st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)

st.divider()

# 3. Accesso con Password
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    pw = st.text_input("Inserisci Password per accedere alla Suite", type="password")
    if pw == st.secrets["password"]:
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.stop()

# 4. Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Funzione per leggere i dati freschi
def get_data():
    return conn.read(ttl=0)

df = get_data()

# --- 5. SEZIONE ANAGRAFICA TOTALE (MODIFICA / AGGIORNA / CANCELLA) ---
st.header("📇 Anagrafica Clienti e Cantieri")
st.write("Modifica le celle, aggiungi righe in fondo o elimina selezionando la riga e premendo 'Canc'.")

# L'editor magico: permette di fare TUTTO
edited_df = st.data_editor(
    df, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="editor_full_anagrafica",
    hide_index=False
)

# Pulsante di salvataggio
if st.button("💾 SALVA MODIFICHE SU GOOGLE SHEET"):
    try:
        conn.update(data=edited_df)
        st.success("✅ Database aggiornato con successo!")
        st.cache_data.clear()
        # Non facciamo il rerun immediato per permettere di vedere il messaggio di successo
    except Exception as e:
        st.error(f"Errore durante il salvataggio: {e}")

# --- 6. VISUALIZZAZIONE RAPIDA ---
st.divider()
st.subheader("🔍 Ricerca Rapida")
search = st.text_input("Inserisci nome cliente o cantiere per filtrare la vista:")
if search:
    filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    st.dataframe(filtered, use_container_width=True)
