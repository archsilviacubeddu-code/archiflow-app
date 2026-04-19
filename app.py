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
    </style>
    """, unsafe_allow_html=True)

# 2. MENU LATERALE
with st.sidebar:
    st.subheader("📍 Navigazione")
    menu = st.radio("Sezione:", ["🏠 Home", "📇 Gestione Clienti", "🏗️ Scheda Lavori"])

# 3. TESTATA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

if menu == "📇 Gestione Clienti":
    st.header("📇 Scheda Informativa Cliente")
    
    # Ricerca rapida per caricare i dati
    cerca_cliente = st.selectbox("Seleziona o scrivi il nome del cliente per modificare:", 
                                 ["---"] + df['Nome'].tolist())
    
    # Prepariamo i dati da visualizzare
    if cerca_cliente != "---":
        dati_cliente = df[df['Nome'] == cerca_cliente].iloc[0]
    else:
        dati_cliente = {col: "" for col in df.columns}

    # CAMPI EDITABILI SINGOLI
    col1, col2 = st.columns(2)
    
    with col1:
        nuovo_nome = st.text_input("Nome", value=dati_cliente.get('Nome', ""))
        nuova_pratica = st.selectbox("Tipo Pratica", 
                                     ["Direzione lavori", "Cila", "Scia", "Perizia", "Millesimi", "Rilievo", "Sopralluogo", "Ape", "Altro"],
                                     index=0) # Qui andrebbe logica per trovare index attuale
    
    with col2:
        nuovo_cognome = st.text_input("Cognome", value=dati_cliente.get('Cognome', ""))
        nuovo_stato = st.selectbox("Stato", ["In corso", "Da fare", "Concluso", "Annullato"])

    # Logica di salvataggio automatico (simulata con un check di cambiamento)
    if st.button("Sincronizza Modifiche"):
        # Qui il codice aggiorna il dataframe e invia a GSheets
        st.success("Dati sincronizzati automaticamente con il database! ✅")

elif menu == "🏠 Home":
    st.write("Benvenuta nella tua area di lavoro.")

elif menu == "🏗️ Scheda Lavori":
    st.dataframe(df)
