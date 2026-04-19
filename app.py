import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

# 1. SETUP E STILE PREMIUM ARCHIFLOW
st.set_page_config(page_title="Archiflow Suite", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div.stButton > button {
        border-radius: 15px; font-weight: bold; height: 5em; 
        background-color: white; border: 2px solid #e2e8f0;
        transition: 0.3s; font-size: 15px !important;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    .stTextInput input { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONNESSIONE DATI E LOGICA ID
# Nota: Assicurati che nel tuo file .streamlit/secrets.toml i permessi siano corretti
conn = st.connection("gsheets", type=GSheetsConnection)

def carica_dati():
    try:
        return conn.read(ttl=0).fillna("")
    except Exception as e:
        st.error(f"Errore nel caricamento dati: {e}")
        return pd.DataFrame()

df = carica_dati()

def genera_nuovo_id(dataframe):
    if dataframe.empty or 'id' not in dataframe.columns:
        return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR FISSA
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.header("🏛️ ARCHIFLOW")
    
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- LOGICA DELLE PAGINE ---

if menu == "🏠 HOME":
    st.title("Benvenuta Silvia 🏠")
    st.write("### Riepilogo Studio")
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Clienti Totali", len(df))
        if 'Stato' in df.columns:
            attive = len(df[df['Stato'] != 'Concluso'])
            col2.metric("Pratiche Attive", attive)
        st.divider()
        st.write("### Ultime Pratiche Inserite")
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("Nessun dato disponibile nel foglio Google.")

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # Ricerca cliente
    cerca = st.text_input("🔍 Cerca cliente esistente o scrivi per nuovo:")
    
    # Filtro dinamico per la selezione
    mask = df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1) if cerca else [True] * len(df)
    df_filtrato = df[mask] if not df.empty else df

    opzioni = ["+ AGGIUNGI NUOVO"] + (df_filtrato['Cliente'].tolist() if 'Cliente' in df.columns else [])
    scelta = st.selectbox("Seleziona per modificare o creare:", opzioni)
    
    # Caricamento dati sotto il cerca
    if scelta == "+ AGGIUNGI NUOVO":
        id_attuale = genera_nuovo_id(df)
        dati_form = {col: "" for col in df.columns} if not df.empty else {"id": "1", "Cliente": ""}
        dati_form['id'] = id_attuale
    else:
        id_attuale = df[df['Cliente'] == scelta]['id'].values[0]
        dati_form = df[df['id'] == id_attuale].iloc[0].to_dict()

    # Form di modifica (Sotto il cerca)
    with st.form("form_anagrafica_completo"):
        st.write(f"### Dati per ID: {id_attuale}")
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Cliente/Ragione Sociale", value=dati_form.get('Cliente', ""))
        cf = c2.text_input("Codice Fiscale / P.IVA", value=dati_form.get('CF_PIVA', ""))
        
        tel = c1.text_input("Telefono", value=dati_form.get('Telefono', ""))
        mail = c2.text_input("Email", value=dati_form.get('Email', ""))
        
        ind = st.text_input("Indirizzo Sede", value=dati_form.get('Indirizzo', ""))
        note_gen = st.text_area("Note Generali", value=dati_form.get('Note_Generali', ""))

        if st.form_submit_button("💾 SALVA MODIFICHE ANAGRAFICA"):
            nuova_riga = dati_form.copy()
            nuova_riga.update({
                "id": id_attuale, "Cliente": nome, "CF_PIVA": cf,
                "Telefono": tel, "Email": mail, "Indirizzo": ind, "Note_Generali": note_gen
            })
            
            try:
                if scelta == "+ AGGIUNGI NUOVO":
                    df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
                else:
                    idx = df[df['id'] == id_attuale].index[0]
                    for k, v in nuova_riga.items(): df.at[idx, k] = v
                
                # Risoluzione errore update: sovrascriviamo il foglio
                conn.update(data=df)
                st.success("Dati sincronizzati su Google Sheets! ✅")
                st.rerun()
            except Exception as e:
                st.error(f"Errore critico durante l'aggiornamento: {e}")
                st.warning("Verifica che il Foglio Google non sia protetto e che le credenziali abbiano permessi di EDIT.")

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Scheda Lavori e Cantieri")
    if not df.empty and 'Cliente' in df.columns:
        cliente_sel = st.selectbox("Seleziona Cliente:", df['Cliente'].tolist())
        idx_l = df[df['Cliente'] == cliente_sel].index[0]
        dati_lavoro = df.iloc[idx_l].to_dict()

        st.write("### 🔘 Tipo di Prestazione (Clicca per impostare)")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        pratica_tipo = dati_lavoro.get('Pratica', "")
        if b1.button("🚧\nDIR.\nLAVORI"): pratica_tipo = "Direzione Lavori"
        if b2.button("📋\nPRATICHE\nCILA/SCIA"): pratica_tipo = "Pratiche"
        if b3.button("📐\nRILIEVI\nINFO"): pratica_tipo = "Rilievi"
        if b4.button("📊\nMILLESIMI"): pratica_tipo = "Millesimi"
        if b5.button("➕\nALTRO"): pratica_tipo = "Altro"

        with st.form("form_lavori_dettaglio"):
            st.info(f"Categoria Attuale: **{pratica_tipo}**")
            c_a, c_b = st.columns(2)
            stato = c_a.selectbox("Stato Pratica", ["Da fare", "In corso", "Concluso", "Sospeso"], index=0)
            scadenza = c_b.text_input("Scadenza / Protocollo", value=dati_lavoro.get('Scadenza', ""))
            note_cantiere = st.text_area("Note Cantiere", value=dati_lavoro.get('Note_Cantiere', ""))
            
            if st.form_submit_button("🚀 AGGIORNA SCHEDA LAVORO"):
                df.at[idx_l, 'Pratica'] = pratica_tipo
                df.at[idx_l, 'Stato'] = stato
                df.at[idx_l, 'Scadenza'] = scadenza
                df.at[idx_l, 'Note_Cantiere'] = note_cantiere
                conn.update(data=df)
                st.success("Scheda Lavoro aggiornata! 🏗️")
                st.rerun()
    else:
        st.warning("Carica prima dei clienti in Anagrafica per gestire i lavori.")
