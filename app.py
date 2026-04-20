import streamlit as st
import pandas as pd
import os
import openai

# 1. SETUP ESTETICO E CONFIGURAZIONE
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

    /* BOTTONI PLANCIA LAVORI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNZIONI AI
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

# 3. DATABASE
DB_ANA = "database_archiflow.csv"
DB_CAN = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "chk_durc", "chk_contratti", "chk_urbanistica", "chk_finelavori", "chk_accatastamento"]

def carica_db(f, c):
    if os.path.exists(f):
        try:
            df = pd.read_csv(f, dtype=str).fillna("")
            for col in c: 
                if col not in df.columns: df[col] = ""
            return df[c]
        except: return pd.DataFrame(columns=c)
    return pd.DataFrame(columns=c)

def salva_db(df, f):
    df.to_csv(f, index=False)

df_ana = carica_db(DB_ANA, COL_ANA)
df_can = carica_db(DB_CAN, COL_CAN)

# 4. SIDEBAR CON LOGO
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.title("ARCHIFLOW")
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

# --- LOGICA PAGINE ---

if menu == "HOME":
    st.title("Archiflow Suite Gestionale")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "add"; st.session_state.ana_sel = None; st.rerun()
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        v = df_ana[["id", "Cliente"]].copy(); v.insert(0, "Sel.", False)
        ed = st.data_editor(v, hide_index=True, use_container_width=True, key="ed_ana")
        sel = ed[ed["Sel."] == True]["id"].tolist()
        if sel and st.button("📂 APRI SCHEDA CLIENTE"):
            st.session_state.modo_ana = "edit"; st.session_state.ana_sel = sel[-1]; st.rerun()
    
    with col_r:
        if st.session_state.get("modo_ana"):
            with st.form("f_ana"):
                id_a = st.session_state.ana_sel
                d = df_ana[df_ana['id'] == id_a].iloc[0].to_dict() if id_a else {c: "" for c in COL_ANA}
                st.subheader(f"Scheda: {d.get('Cliente', 'Nuovo')}")
                new = {"id": id_a if id_a else str(len(df_ana)+1)}
                c1, c2 = st.columns(2)
                for i, c in enumerate(COL_ANA[1:]):
                    new[c] = (c1 if i%2==0 else c2).text_input(c, value=str(d.get(c, "")))
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("✅ AGGIORNA / SALVA"):
                    if not id_a: df_ana = pd.concat([df_ana, pd.DataFrame([new])], ignore_index=True)
                    else: df_ana.loc[df_ana['id'] == id_a] = list(new.values())
                    salva_db(df_ana, DB_ANA); st.rerun()
                if b2.form_submit_button("🗑️ ELIMINA"):
                    df_ana = df_ana[df_ana['id'] != id_a]; salva_db(df_ana, DB_ANA); st.rerun()

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.button("⬅️ TORNA ALLA PLANCIA"): st.session_state.sotto_menu = None; st.session_state.c_aperto = None; st.rerun()
        
        if not st.session_state.get("c_aperto"):
            with st.expander("➕ AGGIUNGI NUOVO CANTIERE"):
                with st.form("n_c"):
                    cl = st.selectbox("Cliente", [""] + df_ana["Cliente"].tolist())
                    ind = st.text_input("Indirizzo")
                    tp = st.radio("Cantiere", ["Interni", "Esterni"], horizontal=True)
                    stat = st.selectbox("Stato", ["Iniziale", "In Corso", "Chiuso"])
                    if st.form_submit_button("CREA CANTIERE"):
                        new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": cl, "Indirizzo": ind, "Tipo": tp, "Stato": stat}
                        df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                        salva_db(df_can, DB_CAN); st.rerun()
            
            st.divider()
            cerca = st.text_input("🔍 Cerca cantiere (Lettera, Cliente o Via):")
            filt = df_can[df_can.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)] if cerca else df_can
            
            for _, r in filt.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                    col1.write(f"**{r['Cliente']}**")
                    col2.write(r['Indirizzo'])
                    col3.write(r['Tipo'])
                    col4.write(r['Stato'])
                    if col5.button("📂 APRI SCHEDA", key=r['id_cantiere']):
                        st.session_state.c_aperto = r['id_cantiere']; st.rerun()
                    st.write("---")
        else:
            id_c = st.session_state.c_aperto
            r = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.subheader(f"📍 {r['Cliente']} - {r['Indirizzo']}")
            if st.button("⬅️ TORNA ALLA LISTA"): st.session_state.c_aperto = None; st.rerun()
            
            with st.form("f_edit_can"):
                t1, t2, t3 = st.tabs(["📋 DATI & CHECKLIST", "🎙️ DIARIO & AI", "⚙️ GESTIONE"])
                with t1:
                    u_ind = st.text_input("Indirizzo", value=r['Indirizzo'])
                    u_tp = st.radio("Tipo", ["Interni", "Esterni"], index=0 if r['Tipo']=="Interni" else 1, horizontal=True)
                    u_stat = st.selectbox("Stato", ["Iniziale", "In Corso", "Chiuso"], index=0)
                    st.write("**Checklist:**")
                    ck1 = st.checkbox("DURC", value=(r['chk_durc']=="1"))
                    ck2 = st.checkbox("Pratica Urbanistica", value=(r['chk_urbanistica']=="1"))
                    ck3 = st.checkbox("Fine Lavori", value=(r['chk_finelavori']=="1"))
                with t2:
                    st.info("🎙️ Registra appunti o salva la conversazione per l'AI.")
                    u_note = st.text_area("Diario di Bordo", value=r['Note'], height=200)
                    if st.form_submit_button("🤖 GENERA VERBALE AI"):
                        st.session_state.verb_res = genera_verbale_ai(u_note, api_key)
                    if "verb_res" in st.session_state:
                        st.text_area("Proposta Verbale AI", value=st.session_state.verb_res, height=300)
                with t3:
                    c_up, c_del = st.columns(2)
                    if c_up.form_submit_button("🔄 AGGIORNA"):
                        idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                        df_can.loc[idx, ['Indirizzo', 'Tipo', 'Stato', 'Note', 'chk_durc', 'chk_urbanistica', 'chk_finelavori']] = [u_ind, u_tp, u_stat, u_note, "1" if ck1 else "0", "1" if ck2 else "0", "1" if ck3 else "0"]
                        salva_db(df_can, DB_CAN); st.success("Aggiornato!"); st.rerun()
                    if c_del.form_submit_button("🗑️ CANCELLA"):
                        df_can = df_can[df_can['id_cantiere'] != id_c]; salva_db(df_can, DB_CAN); st.session_state.c_aperto = None; st.rerun()

    else:
        st.header("🏗️ Selezione Area di Lavoro")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="main_dl", use_container_width=True): st.session_state.sotto_menu = "DL"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-ril">', unsafe_allow_html=True)
            if st.button("📐\nRILIEVI", key="main_ril", use_container_width=True): st.toast("Rilievi")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nCILA/SCIA", use_container_width=True): st.toast("Pratiche")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", use_container_width=True): st.toast("Millesimi")
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True): st.toast("APE")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True): st.toast("Altro")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenze e Consegne")
    st.dataframe(df_ana[["Cliente", "Pratica", "Scadenza"]], use_container_width=True, hide_index=True)
