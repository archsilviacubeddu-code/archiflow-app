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
    /* Stile per la lista cliccabile */
    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 10px; }
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

# --- LOGICA PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Riepilogo Generale")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    col_tasti = st.columns([1, 4])
    if col_tasti[0].button("➕ AGGIUNGI NUOVO"):
        st.session_state.modo = "aggiungi"
        st.session_state.cliente_selezionato = None
        st.rerun()

    st.divider()

    # RICERCA E LISTA CLICCABILE
    col_list, col_form = st.columns([1, 2])

    with col_list:
        st.write("### 🔍 Lista Clienti")
        cerca = st.text_input("Cerca per nome o lettera:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        
        # Lista di pulsanti per ogni cliente
        for _, row in df_f.iterrows():
            if st.button(f"👤 {row['Cliente']}", key=f"btn_{row['id']}", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_selezionato = row['id']
                st.rerun()

    with col_form:
        id_at = st.session_state.get('cliente_selezionato')
        modo = st.session_state.get('modo')

        if modo == "aggiungi":
            id_at = genera_id(df)
            dati_f = {col: "" for col in df.columns}
            st.write(f"### ✨ Nuovo Profilo (ID: {id_at})")
        elif modo == "modifica" and id_at:
            dati_f = df[df['id'] == id_at].iloc[0].to_dict()
            st.write(f"### 📝 Modifica: {dati_f['Cliente']}")
        else:
            st.info("Seleziona un cliente dalla lista a sinistra o clicca su 'Aggiungi Nuovo'")
            st.stop()

        with st.form("form_anagrafica"):
            nuovi_dati = {"id": id_at}
            c1, c2 = st.columns(2)
            
            nuovi_dati["Cliente"] = c1.text_input("Cliente", value=str(dati_f.get("Cliente", "")))
            nuovi_dati["C.F. / P.IVA"] = c2.text_input("C.F. / P.IVA", value=str(dati_f.get("C.F. / P.IVA", "")))
            nuovi_dati["Indirizzo"] = c1.text_input("Indirizzo", value=str(dati_f.get("Indirizzo", "")))
            nuovi_dati["CAP"] = c2.text_input("CAP", value=str(dati_f.get("CAP", "")))
            nuovi_dati["Città"] = c1.text_input("Città", value=str(dati_f.get("Città", "")))
            nuovi_dati["Telefono"] = c2.text_input("Telefono", value=str(dati_f.get("Telefono", "")))
            nuovi_dati["Email"] = c1.text_input("Email", value=str(dati_f.get("Email", "")))
            nuovi_dati["Web"] = c2.text_input("Sito Web", value=str(dati_f.get("Web", "")))
            
            st.divider()
            col_p1, col_p2 = st.columns(2)
            lista_pratiche = ["---", "CILA", "SCIA", "APE", "Legge 10", "Rilievo", "Direzione Lavori", "Progettazione", "Millesimi", "Perizia"]
            p_pre = dati_f.get("Pratica", "")
            scelta_p = col_p1.selectbox("Tipo Pratica", lista_pratiche, index=lista_pratiche.index(p_pre) if p_pre in lista_pratiche else 0)
            manuale_p = col_p2.text_input("Inserimento manuale Pratica:", value=p_pre if p_pre not in lista_pratiche else "")
            nuovi_dati["Pratica"] = manuale_p if manuale_p else scelta_p

            col_s1, col_s2 = st.columns(2)
            lista_stati = ["---", "Da fare", "In corso", "Annullata", "Conclusa"]
            s_pre = dati_f.get("Stato", "")
            scelta_s = col_s1.selectbox("Stato", lista_stati, index=lista_stati.index(s_pre) if s_pre in lista_stati else 0)
            manuale_s = col_s2.text_input("Inserimento manuale Stato:", value=s_pre if s_pre not in lista_stati else "")
            nuovi_dati["Stato"] = manuale_s if manuale_s else scelta_s

            nuovi_dati["Note"] = st.text_area("Note", value=str(dati_f.get("Note", "")))
            
            if st.form_submit_button("✅ CONFERMA"):
                if modo == "aggiungi":
                    df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
                else:
                    idx = df[df['id'] == id_at].index[0]
                    for k, v in nuovi_dati.items(): df.at[idx, k] = v
                
                salva_dati(df)
                st.success("Dati aggiornati!")
                st.session_state.modo = None
                st.rerun()

        if modo == "modifica":
            if st.button("🗑️ ELIMINA CLIENTE"):
                df = df[df['id'] != id_at]
                salva_dati(df)
                st.session_state.modo = None
                st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Operativo")
    cl_lav = st.selectbox("Seleziona Pratica:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write(f"**Cliente:** {cl_lav} | **Stato Attuale:** {lavoro['Stato']}")
        b = st.columns(4)
        nuovo_s = lavoro['Stato']
        if b[0].button("⏳ DA FARE"): nuovo_s = "Da fare"
        if b[1].button("🚧 IN CORSO"): nuovo_s = "In corso"
        if b[2].button("❌ ANNULLATA"): nuovo_s = "Annullata"
        if b[3].button("🏁 CONCLUSA"): nuovo_s = "Conclusa"
        
        if nuovo_s != lavoro['Stato']:
            df.at[idx_l, 'Stato'] = nuovo_s
            salva_dati(df)
            st.rerun()
