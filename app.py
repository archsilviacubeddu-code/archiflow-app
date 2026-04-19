import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
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

# 2. GESTIONE DATABASE LOCALE
DB_FILE = "database_archiflow.csv"

def carica_dati():
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

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Tabella Riepilogativa")
    st.dataframe(df, use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.rerun()

    cerca = st.text_input("🔍 Cerca cliente:")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["---"] + df_f['Cliente'].tolist() if not df_f.empty else ["---"]
    scelta = st.selectbox("Seleziona profilo:", opzioni)

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
        st.info("Seleziona un cliente o clicca su 'Aggiungi Nuovo'")
        st.stop()

    with st.form("form_anagrafica"):
        st.write(f"### Scheda Tecnica ID: {id_at}")
        nuovi_dati = {"id": id_at}
        
        c1, c2 = st.columns(2)
        
        # Campi Base
        nuovi_dati["Cliente"] = c1.text_input("Cliente", value=str(dati_f.get("Cliente", "")))
        nuovi_dati["C.F. / P.IVA"] = c2.text_input("C.F. / P.IVA", value=str(dati_f.get("C.F. / P.IVA", "")))
        nuovi_dati["Indirizzo"] = c1.text_input("Indirizzo", value=str(dati_f.get("Indirizzo", "")))
        nuovi_dati["CAP"] = c2.text_input("CAP", value=str(dati_f.get("CAP", "")))
        nuovi_dati["Città"] = c1.text_input("Città", value=str(dati_f.get("Città", "")))
        nuovi_dati["Telefono"] = c2.text_input("Telefono", value=str(dati_f.get("Telefono", "")))
        nuovi_dati["Email"] = c1.text_input("Email", value=str(dati_f.get("Email", "")))
        nuovi_dati["Web"] = c2.text_input("Sito Web", value=str(dati_f.get("Web", "")))
        
        st.divider()
        
        # SEZIONE PRATICA E STATO CON SPAZIO MANUALE
        st.write("### Dettagli Pratica e Stato")
        col_p1, col_p2 = st.columns([1, 1])
        
        lista_pratiche = ["---", "CILA", "SCIA", "APE", "Legge 10", "Rilievo", "Direzione Lavori", "Progettazione", "Millesimi", "Perizia"]
        p_pre = dati_f.get("Pratica", "")
        scelta_p = col_p1.selectbox("Seleziona Tipo Pratica", lista_pratiche, index=lista_pratiche.index(p_pre) if p_pre in lista_pratiche else 0)
        manuale_p = col_p2.text_input("Oppure scrivi Pratica manualmente:", value=p_pre if p_pre not in lista_pratiche else "")
        nuovi_dati["Pratica"] = manuale_p if manuale_p else scelta_p

        col_s1, col_s2 = st.columns([1, 1])
        lista_stati = ["---", "Da fare", "In corso", "Annullata", "Conclusa"]
        s_pre = dati_f.get("Stato", "")
        scelta_s = col_s1.selectbox("Seleziona Stato", lista_stati, index=lista_stati.index(s_pre) if s_pre in lista_stati else 0)
        manuale_s = col_s2.text_input("Oppure scrivi Stato manualmente:", value=s_pre if s_pre not in lista_stati else "")
        nuovi_dati["Stato"] = manuale_s if manuale_s else scelta_s

        nuovi_dati["Note"] = st.text_area("Note e Protocolli", value=str(dati_f.get("Note", "")))
        
        if st.form_submit_button("✅ CONFERMA"):
            if st.session_state.get('modo') == "aggiungi":
                df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_dati.items(): df.at[idx, k] = v
            
            salva_dati(df)
            st.success("Dati aggiornati! ✅")
            st.session_state.modo = None
            st.rerun()

    if scelta != "---":
        if st.button("🗑️ ELIMINA DEFINITIVAMENTE"):
            df = df[df['id'] != id_at]
            salva_dati(df)
            st.warning("Rimosso.")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Operativo")
    cl_lav = st.selectbox("Seleziona Pratica:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write(f"**Cliente:** {cl_lav} | **Pratica:** {lavoro['Pratica']}")
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
