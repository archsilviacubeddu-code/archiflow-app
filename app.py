import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

# 1. SETUP E STILE PREMIUM
st.set_page_config(page_title="Archiflow Suite", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Pulsanti Categorie GIGANTI */
    div.stButton > button {
        border-radius: 15px; font-weight: bold; height: 6em; 
        background-color: white; border: 2px solid #e2e8f0;
        transition: 0.3s; font-size: 16px !important;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    .stTextInput input { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONNESSIONE E LOGICA ID AUTOMATICO
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).fillna("")

def genera_nuovo_id(dataframe):
    if dataframe.empty or 'id' not in dataframe.columns:
        return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR (LOGO E MENU FISSO)
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.header("🏛️ ARCHIFLOW")
    
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- LOGICA PAGINE ---

if menu == "🏠 HOME":
    st.title("Benvenuta Silvia 🏠")
    st.write("### Riepilogo Studio")
    col1, col2 = st.columns(2)
    col1.metric("Clienti in Anagrafica", len(df))
    col2.metric("Pratiche Attive", len(df[df['Stato'] != 'Concluso']) if 'Stato' in df.columns else 0)
    st.divider()
    st.write("### Ultime attività registrate")
    st.dataframe(df.tail(10), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # Ricerca
    cerca = st.text_input("🔍 Cerca cliente (Nome, Cognome o lettera):")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["+ AGGIUNGI NUOVO"] + df_f['Cliente'].tolist() if 'Cliente' in df.columns else ["+ AGGIUNGI NUOVO"]
    scelta = st.selectbox("Seleziona per modificare o creare:", opzioni)
    
    # Logica caricamento dati sotto il cerca
    if scelta == "+ AGGIUNGI NUOVO":
        id_at = genera_nuovo_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        id_at = df[df['Cliente'] == scelta]['id'].values[0]
        dati_f = df[df['id'] == id_at].iloc[0].to_dict()

    # Form di modifica immediata
    with st.form("form_anagrafica_immediato"):
        st.write(f"**ID: {id_at}**")
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome/Cliente", value=dati_f.get('Cliente', ""))
        n_tel = c2.text_input("Telefono", value=dati_f.get('Telefono', ""))
        n_ind = st.text_input("Indirizzo Sede", value=dati_f.get('Indirizzo', ""))
        n_mail = st.text_input("Email", value=dati_f.get('Email', ""))
        
        if st.form_submit_button("💾 SALVA MODIFICHE ANAGRAFICA"):
            # Prepariamo la riga con tutti i campi esistenti per non perdere nulla
            nuova_r = dati_f.copy()
            nuova_r.update({"id": id_at, "Cliente": n_nome, "Telefono": n_tel, "Indirizzo": n_ind, "Email": n_mail})
            
            if scelta == "+ AGGIUNGI NUOVO":
                df = pd.concat([df, pd.DataFrame([nuova_r])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuova_r.items(): df.at[idx, k] = v
            
            conn.update(data=df)
            st.success("Anagrafica aggiornata correttamente! ✅")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Lavori")
    
    cl_lav = st.selectbox("Seleziona Cliente:", df['Cliente'].tolist() if not df.empty else [])
    
    if cl_lav:
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write("### 🔘 Categoria Lavoro (Clicca per cambiare)")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        # Stato temporaneo per la pratica
        p_tipo = lavoro.get('Pratica', "")
        if b1.button("🚧\nDIR.\nLAVORI"): p_tipo = "Direzione Lavori"
        if b2.button("📋\nPRATICHE\nCILA/SCIA"): p_tipo = "Pratiche"
        if b3.button("📐\nRILIEVI\nINFO"): p_tipo = "Rilievi"
        if b4.button("📊\nMILLESIMI"): p_tipo = "Millesimi"
        if b5.button("➕\nALTRO"): p_tipo = "Altro"
        
        with st.form("form_lavoro_dettaglio"):
            st.info(f"Tipo selezionato: **{p_tipo}**")
            c_a, c_b = st.columns(2)
            st_lav = c_a.selectbox("Stato Avanzamento", ["Da fare", "In corso", "Concluso"], index=0)
            scad = c_b.text_input("Scadenza", value=lavoro.get('Scadenza', ""))
            note_lav = st.text_area("Note di cantiere", value=lavoro.get('Note', ""))
            
            if st.form_submit_button("🚀 AGGIORNA SCHEDA LAVORO"):
                df.at[idx_l, 'Pratica'] = p_tipo
                df.at[idx_l, 'Stato'] = st_lav
                df.at[idx_l, 'Scadenza'] = scad
                df.at[idx_l, 'Note'] = note_lav
                conn.update(data=df)
                st.success("Lavoro sincronizzato su Sheets! 🏗️")
                st.rerun()
