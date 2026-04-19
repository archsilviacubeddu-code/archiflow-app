import streamlit as st
import pandas as pd
import os

# 1. SETUP APPLICAZIONE
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div.stButton > button {
        border-radius: 12px; font-weight: bold; height: 4em; 
        background-color: white; border: 2px solid #e2e8f0;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    .stTextInput input, .stSelectbox { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIONE DATABASE LOCALE (CSV)
DB_FILE = "database_archiflow.csv"

def carica_dati():
    # Definiamo le colonne nell'ordine esatto richiesto
    colonne = [
        "id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", 
        "Telefono", "Email", "Web", "Pratica", "Stato", "Note"
    ]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
    else:
        return pd.DataFrame(columns=colonne)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

def genera_id(dataframe):
    if dataframe.empty: return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR (LOGO E MENU)
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Riepilogo Pratiche")
    st.dataframe(df, use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # PULSANTE AGGIUNGI
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.rerun()

    st.divider()

    # RICERCA E SELEZIONE
    cerca = st.text_input("🔍 Cerca cliente:")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["---"] + df_f['Cliente'].tolist() if not df_f.empty else ["---"]
    scelta = st.selectbox("Seleziona profilo da gestire:", opzioni)

    if scelta != "---":
        st.session_state.modo = "modifica"
        riga = df[df['Cliente'] == scelta].iloc[0]
        id_at = riga['id']
        dati_f = riga.to_dict()
    elif st.session_state.get('modo') == "aggiungi":
        id_at = genera_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        st.info("Usa il tasto in alto per un nuovo cliente o seleziona un profilo esistente.")
        st.stop()

    # FORM DI INSERIMENTO/MODIFICA
    with st.form("form_anagrafica"):
        st.write(f"### Scheda Tecnica ID: {id_at}")
        nuovi_dati = {"id": id_at}
        
        c1, c2 = st.columns(2)
        
        # Ordine campi richiesto
        nuovi_dati["Cliente"] = c1.text_input("Cliente", value=str(dati_f.get("Cliente", "")))
        nuovi_dati["C.F. / P.IVA"] = c2.text_input("C.F. / P.IVA", value=str(dati_f.get("C.F. / P.IVA", "")))
        
        nuovi_dati["Indirizzo"] = c1.text_input("Indirizzo", value=str(dati_f.get("Indirizzo", "")))
        nuovi_dati["CAP"] = c2.text_input("CAP", value=str(dati_f.get("CAP", "")))
        
        nuovi_dati["Città"] = c1.text_input("Città", value=str(dati_f.get("Città", "")))
        nuovi_dati["Telefono"] = c2.text_input("Telefono", value=str(dati_f.get("Telefono", "")))
        
        nuovi_dati["Email"] = c1.text_input("Email", value=str(dati_f.get("Email", "")))
        nuovi_dati["Web"] = c2.text_input("Sito Web", value=str(dati_f.get("Web", "")))
        
        # Campi a scelta fissa (Pratica e Stato)
        lista_pratiche = ["CILA", "SCIA", "APE", "Legge 10", "Rilievo", "Direzione Lavori", "Progettazione", "Millesimi", "Perizia", "Altro"]
        p_val = dati_f.get("Pratica", "Altro")
        nuovi_dati["Pratica"] = c1.selectbox("Tipo Pratica", lista_pratiche, index=lista_pratiche.index(p_val) if p_val in lista_pratiche else 9)
        
        lista_stati = ["Da fare", "In corso", "Annullata", "Conclusa"]
        s_val = dati_f.get("Stato", "Da fare")
        nuovi_dati["Stato"] = c2.selectbox("Stato", lista_stati, index=lista_stati.index(s_val) if s_val in lista_stati else 0)
        
        nuovi_dati["Note"] = st.text_area("Note", value=str(dati_f.get("Note", "")))
        
        st.divider()
        if st.form_submit_button("✅ CONFERMA"):
            if st.session_state.get('modo') == "aggiungi":
                df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_dati.items(): df.at[idx, k] = v
            
            salva_dati(df)
            st.success("Archiviato correttamente! ✅")
            st.session_state.modo = None
            st.rerun()

    if scelta != "---":
        if st.button("🗑️ ELIMINA CLIENTE"):
            df = df[df['id'] != id_at]
            salva_dati(df)
            st.warning("Profilo rimosso.")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Operativo")
    # Qui puoi gestire velocemente lo stato dei lavori con i bottoni grandi
    cl_lav = st.selectbox("Seleziona Pratica:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write(f"### Gestione Rapida: {cl_lav}")
        # Bottoni giganti per aggiornare lo Stato
        st.write("Aggiorna Stato:")
        b = st.columns(4)
        nuovo_s = lavoro['Stato']
        if b[0].button("⏳\nDA FARE"): nuovo_s = "Da fare"
        if b[1].button("🚧\nIN CORSO"): nuovo_s = "In corso"
        if b[2].button("❌\nANNULLATA"): nuovo_s = "Annullata"
        if b[3].button("🏁\nCONCLUSA"): nuovo_s = "Conclusa"
        
        if nuovo_s != lavoro['Stato']:
            df.at[idx_l, 'Stato'] = nuovo_s
            salva_dati(df)
            st.rerun()
