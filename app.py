import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAZIONE E STILE
st.set_page_config(page_title="Archiflow Suite", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Titoli e Testata */
    .titolo-destra { text-align: right; color: #1e293b; font-family: 'Helvetica'; margin-bottom: 0; }
    .sottotitolo-destra { text-align: right; color: #64748b; font-size: 1.1rem; margin-top: 0; }
    /* Pulsanti Categorie GIGANTI */
    div.stButton > button {
        border-radius: 15px; font-weight: bold; height: 6em; 
        background-color: white; border: 2px solid #e2e8f0;
        transition: 0.3s; font-size: 16px !important;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    /* Campi input puliti */
    .stTextInput input { border-radius: 10px !important; padding: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).fillna("")

# 3. SIDEBAR CON LOGO
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.header("🏛️ ARCHIFLOW")
    st.divider()
    menu = st.radio("MENU PRINCIPALE:", ["📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# TESTATA FISSA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# --- PAGINA ANAGRAFICA ---
if menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # CERCA
    cerca = st.text_input("🔍 Cerca cliente (Nome, Cognome o lettera):")
    df_mostra = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    # SELEZIONE CLIENTE PER MODIFICA
    if not df_mostra.empty:
        scelta = st.selectbox("Seleziona il cliente da modificare:", df_mostra['Cliente'].tolist())
        idx = df[df['Cliente'] == scelta].index[0]
        riga = df.iloc[idx].to_dict()

        # CAMPI EDITABILI (PULITI)
        st.write("### 📝 Dati Cliente")
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome/Ragione Sociale", value=riga.get('Cliente', ""))
        cf = c2.text_input("Codice Fiscale / P.IVA", value=riga.get('CF_PIVA', ""))
        
        c3, c4 = st.columns(2)
        tel = c3.text_input("Telefono", value=riga.get('Telefono', ""))
        mail = c4.text_input("Email", value=riga.get('Email', ""))
        
        ind = st.text_input("Indirizzo Sede", value=riga.get('Indirizzo', ""))
        
        # AZIONI
        col_a, col_b = st.columns(2)
        if col_a.button("💾 AGGIORNA DATI"):
            df.at[idx, 'Cliente'] = nome
            df.at[idx, 'CF_PIVA'] = cf
            df.at[idx, 'Telefono'] = tel
            df.at[idx, 'Email'] = mail
            df.at[idx, 'Indirizzo'] = ind
            conn.update(data=df)
            st.success("Dati aggiornati! ✅")
            st.rerun()
            
        if col_b.button("🗑️ CANCELLA CLIENTE"):
            df = df.drop(idx).reset_index(drop=True)
            conn.update(data=df)
            st.warning("Cliente eliminato.")
            st.rerun()
    
    st.divider()
    st.subheader("📊 Lista Completa")
    st.dataframe(df_mostra, use_container_width=True)

# --- PAGINA SCHEDA LAVORI ---
elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Scheda Lavori e Cantieri")
    
    cliente_lavoro = st.selectbox("Seleziona Cliente/Cantiere:", df['Cliente'].tolist())
    idx_l = df[df['Cliente'] == cliente_lavoro].index[0]
    lavoro = df.iloc[idx_l].to_dict()

    # BOTTONI CATEGORIA
    st.write("### 🔘 Tipo di Prestazione")
    b1, b2, b3, b4, b5 = st.columns(5)
    
    nuova_pratica = lavoro.get('Pratica', "")
    if b1.button("🚧\nDIREZIONE\nLAVORI"): nuova_pratica = "Direzione Lavori"
    if b2.button("📋\nPRATICHE\n(CILA/SCIA)"): nuova_pratica = "Pratiche"
    if b3.button("📐\nRILIEVI\nINFO"): nuova_pratica = "Rilievi"
    if b4.button("📊\nMILLESIMI"): nuova_pratica = "Millesimi"
    if b5.button("➕\nALTRO"): nuova_pratica = "Altro"

    st.info(f"Categoria attuale: **{nuova_pratica}**")

    # CAMPI EDITABILI LAVORO
    st.write("### 📝 Dettagli Pratica")
    ca, cb = st.columns(2)
    stato = ca.selectbox("Stato", ["Da fare", "In corso", "Concluso", "Annullato"], 
                         index=["Da fare", "In corso", "Concluso", "Annullato"].index(lavoro['Stato']) if lavoro['Stato'] in ["Da fare", "In corso", "Concluso", "Annullato"] else 0)
    scadenza = cb.text_input("Scadenza (GG/MM/AAAA)", value=lavoro.get('Scadenza', ""))
    
    note = st.text_area("Note Cantiere", value=lavoro.get('Note', ""))

    if st.button("🚀 SINCRONIZZA SCHEDA LAVORO"):
        df.at[idx_l, 'Pratica'] = nuova_pratica
        df.at[idx_l, 'Stato'] = stato
        df.at[idx_l, 'Scadenza'] = scadenza
        df.at[idx_l, 'Note'] = note
        conn.update(data=df)
        st.success("Scheda lavoro salvata! 🏛️")
