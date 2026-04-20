import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* MENU SIDEBAR */
    .sidebar-btn > div > button {
        height: 4.5em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: 0.3s !important;
    }
    .sidebar-btn > div > button:hover { 
        border-color: #3b82f6 !important; 
        color: #3b82f6 !important;
        background-color: #f0f7ff !important;
    }

    /* BOTTONI LAVORI GIGANTI E COLORATI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }

    .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-2px); transition: 0.2s; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIONE DATABASE (CSV)
DB_ANA = "database_archiflow.csv"
DB_CAN = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo Cantiere", "Stato", "Note Tecniche"]

def carica_db(file, colonne):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, dtype=str).fillna("")
            for col in colonne:
                if col not in df.columns: df[col] = ""
            return df[colonne]
        except: return pd.DataFrame(columns=colonne)
    return pd.DataFrame(columns=colonne)

def salva_db(df, file):
    df.to_csv(file, index=False)

df_ana = carica_db(DB_ANA, COL_ANA)
df_can = carica_db(DB_CAN, COL_CAN)

# 3. SIDEBAR CON LOGO
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.title("ARCHIFLOW")
    st.divider()
    
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"

    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): 
        st.session_state.menu_sel = "HOME"
        st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): 
        st.session_state.menu_sel = "ANAGRAFICA"
        st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): 
        st.session_state.menu_sel = "LAVORI"
        st.session_state.sotto_menu = None # Resetta sottoviste
        st.rerun()
    if st.button("📅 SCADENZE", use_container_width=True): 
        st.session_state.menu_sel = "SCADENZE"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA PAGINE ---

if menu == "HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.subheader("Database Clienti Attivi")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "aggiungi"
        st.session_state.ana_sel = None
        st.rerun()

    col_list, col_form = st.columns([1, 2])
    with col_list:
        st.subheader("Lista Selezionabile")
        if not df_ana.empty:
            df_view = df_ana[["id", "Cliente"]].copy()
            df_view.insert(0, "Seleziona", False)
            edit = st.data_editor(df_view, hide_index=True, disabled=["id", "Cliente"], use_container_width=True, key="editor_ana")
            sel_ids = edit[edit["Seleziona"] == True]["id"].tolist()
            if sel_ids:
                if st.button(f"📂 Apri Scheda ({len(sel_ids)})", use_container_width=True):
                    st.session_state.modo_ana = "modifica"
                    st.session_state.ana_sel = sel_ids[-1]
                    st.rerun()
        else: st.info("Nessun cliente presente.")

    with col_form:
        modo = st.session_state.get("modo_ana")
        id_at = st.session_state.get("ana_sel")
        if modo:
            with st.form("form_ana_detail"):
                dati = df_ana[df_ana['id'] == id_at].iloc[0].to_dict() if modo == "modifica" else {c: "" for c in COL_ANA}
                st.write(f"### Dettaglio Cliente ID: {id_at if id_at else 'Nuovo'}")
                new_data = {"id": id_at if id_at else str(len(df_ana)+1)}
                c1, c2 = st.columns(2)
                for i, col in enumerate(COL_ANA[1:]):
                    new_data[col] = (c1 if i%2==0 else c2).text_input(col, value=str(dati.get(col, "")))
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("✅ SALVA / AGGIORNA", use_container_width=True):
                    if modo == "aggiungi": df_ana = pd.concat([df_ana, pd.DataFrame([new_data])], ignore_index=True)
                    else: df_ana.loc[df_ana['id'] == id_at] = list(new_data.values())
                    salva_db(df_ana, DB_ANA); st.rerun()
                if b2.form_submit_button("🗑️ ELIMINA", use_container_width=True):
                    df_ana = df_ana[df_ana['id'] != id_at]
                    salva_db(df_ana, DB_ANA); st.session_state.modo_ana = None; st.rerun()

elif menu == "LAVORI":
    # SOTTO-MENU DIREZIONE LAVORI
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.button("⬅️ TORNA ALLA PLANCIA LAVORI"):
            st.session_state.sotto_menu = None
            st.rerun()
        
        # 1. AGGIUNGI NUOVO CANTIERE (Stessa struttura di anagrafica)
        with st.expander("➕ AGGIUNGI NUOVO CANTIERE"):
            with st.form("form_new_cantiere"):
                cli_can = st.selectbox("Seleziona Cliente (da Anagrafica)", [""] + df_ana["Cliente"].tolist())
                ind_can = st.text_input("Indirizzo del Cantiere (Via/N.Civico)")
                tipo_can = st.radio("Tipologia Cantiere", ["Interni", "Esterni"], horizontal=True)
                stato_can = st.selectbox("Stato Avanzamento", ["Sopralluogo", "In Corso", "Sospeso", "Chiuso"])
                note_can = st.text_area("Note e Appunti Cantiere")
                
                if st.form_submit_button("REGISTRA CANTIERE"):
                    if cli_can and ind_can:
                        new_c = {
                            "id_cantiere": str(len(df_can)+1),
                            "Cliente": cli_can,
                            "Indirizzo": ind_can,
                            "Tipo Cantiere": tipo_can,
                            "Stato": stato_can,
                            "Note Tecniche": note_can
                        }
                        df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                        salva_db(df_can, DB_CAN)
                        st.success("Cantiere registrato!")
                        st.rerun()
                    else: st.error("Inserire almeno Cliente e Indirizzo.")

        st.divider()

        # 2. RICERCA E LISTA CANTIERI
        st.subheader("Elenco Cantieri Attivi")
        cerca_can = st.text_input("🔍 Cerca per Cliente, Via o Stato")
        
        # Filtro logico
        if cerca_can:
            mask = df_can.apply(lambda row: cerca_can.lower() in row.astype(str).str.lower().values, axis=1)
            df_filt = df_can[mask]
        else:
            df_filt = df_can

        if not df_filt.empty:
            # Header tabella manuale
            h1, h2, h3, h4, h5 = st.columns([2, 2, 1, 1, 1])
            h1.write("**CLIENTE**")
            h2.write("**INDIRIZZO**")
            h3.write("**TIPO**")
            h4.write("**STATO**")
            h5.write("**AZIONE**")
            st.divider()

            for _, row in df_filt.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
                c1.write(row["Cliente"])
                c2.write(row["Indirizzo"])
                c3.write(f"🏠 {row['Tipo Cantiere']}")
                c4.write(f"🟢 {row['Stato']}")
                if c5.button("📂 APRI SCHEDA", key=f"btn_{row['id_cantiere']}"):
                    st.toast(f"Apertura Cantiere ID: {row['id_cantiere']}")
                st.write("---")
        else:
            st.info("Nessun cantiere trovato o registrato.")

    else:
        # PLANCIA GENERALE LAVORI (6 BOTTONI)
        st.header("🏗️ Selezione Area di Lavoro")
        st.write("## ")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="main_dl", use_container_width=True): 
                st.session_state.sotto_menu = "DL"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-ril">', unsafe_allow_html=True)
            if st.button("📐\nRILIEVI", key="main_ril", use_container_width=True): st.toast("Rilievi")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nCILA/SCIA", key="main_pra", use_container_width=True): st.toast("Pratiche")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", key="main_mill", use_container_width=True): st.toast("Millesimi")
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", key="main_ape", use_container_width=True): st.toast("APE/Legge 10")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", key="main_alt", use_container_width=True): st.toast("Altro")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenze e Consegne")
    if not df_ana.empty:
        st.dataframe(df_ana[["Cliente", "Pratica", "Scadenza", "Stato"]], use_container_width=True, hide_index=True)
    else: st.info("Nessun dato in anagrafica.")
