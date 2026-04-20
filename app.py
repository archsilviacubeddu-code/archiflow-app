import streamlit as st
import pandas as pd
import os
import openai

# Prova a importare il registratore vocale
try:
    from streamlit_mic_recorder import mic_recorder
    HAS_MIC = True
except:
    HAS_MIC = False

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
    }

    /* BOTTONI LAVORI GIGANTI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }

    /* HEADER TABELLA */
    .table-header { background-color: #f1f5f9; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 5px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE E FUNZIONI AI
DB_FILE = "database_archiflow.csv"
DB_CANTIERI = "cantieri.csv"
COLONNE = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "chk_durc", "chk_urbanistica", "chk_finelavori"]

def genera_verbale_ai(testo, key):
    if not key: return "Inserisci API Key nella sidebar."
    try:
        client = openai.OpenAI(api_key=key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Sei l'Architetto Silvia Cubeddu. Trasforma gli appunti di cantiere in un verbale tecnico professionale."},
                      {"role": "user", "content": testo}]
        )
        return res.choices[0].message.content
    except Exception as e: return f"Errore AI: {e}"

def carica_dati(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for col in colonne:
            if col not in df.columns: df[col] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

df = carica_dati(DB_FILE, COLONNE)
df_can = carica_dati(DB_CANTIERI, COL_CAN)

# 3. SIDEBAR CON LOGO
with st.sidebar:
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
    else: st.title("ARCHIFLOW")
    st.divider()
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    st.divider()
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()
    if st.button("📅 SCADENZE", use_container_width=True): st.session_state.menu_sel = "SCADENZE"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA ---

if menu == "HOME":
    st.title("Archiflow Dashboard")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"; st.session_state.cliente_sel = None; st.rerun()

    cerca_ana = st.text_input("🔍 Cerca Cliente (Nome o ID):")
    df_filt_ana = df[df.apply(lambda r: cerca_ana.lower() in r.astype(str).str.lower().values, axis=1)] if cerca_ana else df

    col_list, col_form = st.columns([1, 2])
    with col_list:
        if not df_filt_ana.empty:
            df_sel = df_filt_ana[["id", "Cliente"]].copy()
            df_sel.insert(0, "Seleziona", False)
            edited_df = st.data_editor(df_sel, hide_index=True, disabled=["id", "Cliente"], use_container_width=True, key="sel_ana")
            selected_ids = edited_df[edited_df["Seleziona"] == True]["id"].tolist()
            if selected_ids and st.button(f"📂 Apri Scheda", use_container_width=True):
                st.session_state.modo = "modifica"; st.session_state.cliente_sel = selected_ids[-1]; st.rerun()

    with col_form:
        modo = st.session_state.get('modo')
        if modo:
            id_at = st.session_state.get('cliente_sel')
            dati_f = df[df['id'] == id_at].iloc[0].to_dict() if id_at else {c: "" for c in COLONNE}
            with st.form("form_ana"):
                st.write(f"### Dettagli ID: {id_at if id_at else 'Nuovo'}")
                nuovi = {"id": id_at if id_at else str(len(df)+1)}
                c1, c2 = st.columns(2)
                for i, col in enumerate(COLONNE[1:]):
                    nuovi[col] = (c1 if i % 2 == 0 else c2).text_input(col, value=str(dati_f.get(col, "")))
                
                st.write("---")
                b1, b2 = st.columns(2)
                if b1.form_submit_button("✅ AGGIORNA / SALVA", use_container_width=True):
                    if modo == "aggiungi": df = pd.concat([df, pd.DataFrame([nuovi])], ignore_index=True)
                    else: df.loc[df['id'] == id_at] = list(nuovi.values())
                    df.to_csv(DB_FILE, index=False); st.success("Salvato!"); st.rerun()
                if b2.form_submit_button("🗑️ ELIMINA CLIENTE", use_container_width=True):
                    df = df[df['id'] != id_at]; df.to_csv(DB_FILE, index=False); st.warning("Eliminato."); st.session_state.modo = None; st.rerun()

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            r = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.subheader(f"📂 {r['Cliente']} - {r['Indirizzo']}")
            if st.button("⬅️ Torna alla Lista"): st.session_state.c_aperto = None; st.rerun()
            
            with st.container():
                tab1, tab2 = st.tabs(["📋 Documenti", "🎙️ Diario & AI"])
                with tab1:
                    ck1 = st.checkbox("DURC", value=(r['chk_durc']=="1"))
                    ck2 = st.checkbox("Pratica Urbanistica", value=(r['chk_urbanistica']=="1"))
                    ck3 = st.checkbox("Fine Lavori", value=(r['chk_finelavori']=="1"))
                with tab2:
                    if HAS_MIC: audio = mic_recorder(start_prompt="🎤 Registra", stop_prompt="🛑 Salva", key='rec_can')
                    u_note = st.text_area("Note Sopralluogo:", value=r['Note'], height=200)
                    if st.button("🤖 Genera Verbale AI"):
                        st.session_state.v_res = genera_verbale_ai(u_note, api_key)
                    if "v_res" in st.session_state: st.text_area("Verbale AI:", value=st.session_state.v_res, height=250)
                
                if st.button("💾 Salva Note e Stato"):
                    idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                    df_can.at[idx, 'Note'] = u_note
                    df_can.at[idx, 'chk_durc'] = "1" if ck1 else "0"
                    df_can.at[idx, 'chk_urbanistica'] = "1" if ck2 else "0"
                    df_can.at[idx, 'chk_finelavori'] = "1" if ck3 else "0"
                    df_can.to_csv(DB_CANTIERI, index=False); st.success("Salvato!")
        else:
            if st.button("➕ AGGIUNGI NUOVO CANTIERE"):
                new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": "Nuovo", "Indirizzo": "-", "Tipo": "Interni", "Stato": "Da iniziare"}
                df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                df_can.to_csv(DB_CANTIERI, index=False); st.rerun()

            cerca_c = st.text_input("🔍 Cerca Cantiere (Cliente o Via):")
            st.markdown('<div class="table-header">CLIENTE | INDIRIZZO | TIPO | STATO | AZIONI</div>', unsafe_allow_html=True)
            
            filt = df_can[df_can.apply(lambda r: cerca_c.lower() in r.astype(str).str.lower().values, axis=1)] if cerca_c else df_can
            for i, r in filt.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 2.5])
                u_cli = col1.text_input("C", r['Cliente'], key=f"c_{i}", label_visibility="collapsed")
                u_ind = col2.text_input("I", r['Indirizzo'], key=f"i_{i}", label_visibility="collapsed")
                u_tp = col3.selectbox("T", ["Interni", "Esterni"], index=0 if r['Tipo']=="Interni" else 1, key=f"t_{i}", label_visibility="collapsed")
                u_st = col4.selectbox("S", ["Da iniziare", "In corso", "Sospeso", "Ultimato"], index=["Da iniziare", "In corso", "Sospeso", "Ultimato"].index(r['Stato']) if r['Stato'] in ["Da iniziare", "In corso", "Sospeso", "Ultimato"] else 0, key=f"s_{i}", label_visibility="collapsed")
                
                c_a1, c_a2, c_a3 = col5.columns(3)
                if c_a1.button("🔄", key=f"up_{i}"):
                    df_can.loc[i, ['Cliente', 'Indirizzo', 'Tipo', 'Stato']] = [u_cli, u_ind, u_tp, u_st]
                    df_can.to_csv(DB_CANTIERI, index=False); st.rerun()
                if c_a2.button("📂", key=f"op_{i}"):
                    st.session_state.c_aperto = r['id_cantiere']; st.rerun()
                if c_a3.button("🗑️", key=f"del_{i}"):
                    df_can.drop(i).to_csv(DB_CANTIERI, index=False); st.rerun()
            if st.button("⬅️ Esci"): st.session_state.sotto_menu = None; st.rerun()
    else:
        st.header("🏗️ Selezione Area di Lavoro")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="dl_main", use_container_width=True): st.session_state.sotto_menu = "DL"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("📐 RILIEVI", use_container_width=True): st.toast("Rilievi")
        with c2:
            if st.button("📋 PRATICHE", use_container_width=True): st.toast("Pratiche")
            if st.button("📊 MILLESIMI", use_container_width=True): st.toast("Millesimi")
        with c3:
            if st.button("⚡ APE", use_container_width=True): st.toast("APE")
            if st.button("➕ ALTRO", use_container_width=True): st.toast("Altro")

elif menu == "SCADENZE":
    st.header("📅 Scadenze")
    st.dataframe(df[["Cliente", "Pratica", "Scadenza", "Stato"]], use_container_width=True, hide_index=True)
