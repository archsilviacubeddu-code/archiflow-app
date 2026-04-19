import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Pulsanti Categorie GIGANTI */
    div.stButton > button {
        border-radius: 12px; font-weight: bold; height: 6em; 
        background-color: white; border: 2px solid #e2e8f0;
        transition: 0.3s; font-size: 16px !important;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    /* Input di testo puliti */
    .stTextInput input { border-radius: 8px !important; border: 1px solid #d1d5db !important; padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONNESSIONE DATI E LOGICA ID
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).fillna("")

def genera_nuovo_id(dataframe):
    if dataframe.empty or 'id' not in dataframe.columns:
        return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR (LOGO E MENU)
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.error("⚠️ File 'Logo.png' non trovato")
    
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- LOGICA DELLE PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Stato del Registro")
    st.dataframe(df.tail(10), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # Ricerca cliente
    cerca = st.text_input("🔍 Cerca cliente (Nome, Cognome o lettera):")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["+ AGGIUNGI NUOVO"] + (df_f['Cliente'].tolist() if 'Cliente' in df.columns else [])
    scelta = st.selectbox("Seleziona cliente:", opzioni)
    
    # Caricamento dati sotto il cerca (EDITABILE IN BOX, NON CELLE)
    if scelta == "+ AGGIUNGI NUOVO":
        id_at = genera_nuovo_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        id_at = df[df['Cliente'] == scelta]['id'].values[0]
        dati_f = df[df['id'] == id_at].iloc[0].to_dict()

    with st.form("form_modifica_anagrafica"):
        st.write(f"### Scheda ID: {id_at}")
        nuovi_valori = {}
        
        # Genera un box di testo per ogni colonna del tuo Google Sheet
        col_left, col_right = st.columns(2)
        for i, colonna in enumerate(df.columns):
            if colonna.lower() == 'id':
                nuovi_valori[colonna] = id_at
                continue
            
            target_col = col_left if i % 2 == 0 else col_right
            # Qui modifichi il valore direttamente nel box
            nuovi_valori[colonna] = target_col.text_input(f"{colonna}", value=str(dati_f.get(colonna, "")))
        
        st.divider()
        if st.form_submit_button("💾 SALVA TUTTO SU GOOGLE SHEETS"):
            if scelta == "+ AGGIUNGI NUOVO":
                df = pd.concat([df, pd.DataFrame([nuovi_valori])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_valori.items():
                    df.at[idx, k] = v
            
            conn.update(data=df)
            st.success("Dati sincronizzati correttamente! ✅")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Lavori")
    cl_lav = st.selectbox("Seleziona Cliente:", df['Cliente'].tolist() if not df.empty else [])
    
    if cl_lav:
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write("### 🔘 Tipo di Pratica")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        p_tipo = lavoro.get('Pratica', "")
        if b1.button("🚧\nDIR.\nLAVORI"): p_tipo = "Direzione Lavori"
        if b2.button("📋\nPRATICHE\nCILA/SCIA"): p_tipo = "Pratiche"
        if b3.button("📐\nRILIEVI\nINFO"): p_tipo = "Rilievi"
        if b4.button("📊\nMILLESIMI"): p_tipo = "Millesimi"
        if b5.button("➕\nALTRO"): p_tipo = "Altro"
        
        with st.form("form_lavori_box"):
            st.info(f"Pratica impostata: **{p_tipo}**")
            stato = st.selectbox("Stato", ["Da fare", "In corso", "Concluso"], index=0)
            note = st.text_area("Note e Protocolli", value=lavoro.get('Note', ""))
            
            if st.form_submit_button("🚀 AGGIORNA SU SHEETS"):
                df.at[idx_l, 'Pratica'] = p_tipo
                df.at[idx_l, 'Stato'] = stato
                df.at[idx_l, 'Note'] = note
                conn.update(data=df)
                st.success("Scheda lavoro aggiornata! ✅")
                st.rerun()
