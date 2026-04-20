import streamlit as st
import pandas as pd
import os
import openai

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
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
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .cantiere-card { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #e2e8f0; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

def genera_verbale_ai(testo_appunti, api_key):
    if not api_key:
        return "Errore: Inserisci la API Key nella sidebar per usare l'AI."
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei l'Architetto Silvia Cubeddu. Trasforma gli appunti di cantiere in un verbale di sopralluogo professionale, formale e strutturato."},
                {"role": "user", "content": f"Trasforma questi appunti in un verbale formale: {testo_appunti}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore AI: {str(e)}"

DB_ANA = "database_archiflow.csv"
DB_CAN = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Progresso", "Onorario", "Acconti", "Impresa", "Note", 
           "chk_durc", "chk_contratti", "chk_urbanistica", "chk_finelavori", "chk_accatastamento"]

def carica_db(file, colonne):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, dtype=str).fillna("")
            for col in colonne:
                if col not in df.columns: df[col] = "0" if "chk_" in col or col in ["Progresso", "Onorario", "Acconti"] else ""
            return df[colonne]
        except: return pd.DataFrame(columns=colonne)
    return pd.DataFrame(columns=colonne)

def salva_db(df, file):
    df.to_csv(file, index=False)

df_ana = carica_db(DB_ANA, COL_ANA)
df_can = carica_db(DB_CAN, COL_CAN)

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

if menu == "HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.subheader("Database Clienti")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "aggiungi"; st.session_state.ana_sel = None; st.rerun()
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        df_v = df_ana[["id", "Cliente"]].copy(); df_v.insert(0, "Sel.", False)
        ed = st.data_editor(df_v, hide_index=True, use_container_width=True, key="ana_ed")
        sel = ed[ed["Sel."] == True]["id"].tolist()
        if sel and st.button("📂 APRI SCHEDA"):
            st.session_state.modo_ana = "modifica"; st.session_state.ana_sel = sel[-1]; st.rerun()

    with col_r:
        if st.session_state.get("modo_ana"):
            with st.form("form_ana"):
                id_a = st.session_state.ana_sel
                d = df_ana[df_ana['id'] == id_a].iloc[0].to_dict() if id_a else {c: "" for c in COL_ANA}
                new_d = {"id": id_a if id_a else str(len(df_ana)+1)}
                c1, c2 = st.columns(2)
                for i, c in enumerate(COL_ANA[1:]):
                    new_d[c] = (c1 if i%2==0 else c2).text_input(c, value=str(d.get(c, "")))
                if st.form_submit_button("SALVA"):
                    if not id_a: df_ana = pd.concat([df_ana, pd.DataFrame([new_d])], ignore_index=True)
                    else: df_ana.loc[df_ana['id'] == id_a] = list(new_d.values())
                    salva_db(df_ana, DB_ANA); st.rerun()

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        if st.session_state.get("cantiere_aperto"):
            id_c = st.session_state.cantiere_aperto
            row = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.header(f"🏗️ Cantiere: {row['Cliente']}")
            if st.button("⬅️ TORNA"): st.session_state.cantiere_aperto = None; st.rerun()
            t1, t2, t3, t4 = st.tabs(["📊 STATO", "💰 ECONOMIA", "🎙️ VOCALE & AI", "📋 CHECKLIST"])
            with t1:
                prog = st.slider("Avanzamento (%)", 0, 100, int(row['Progresso']))
                st.progress(prog / 100)
                nuovo_stato = st.selectbox("Stato", ["Iniziale", "In Corso", "Sospeso", "Ultimato"], index=0)
            with t2:
                c1, c2, c3 = st.columns(3)
                onorario = c1.number_input("Onorario Totale (€)", value=float(row['Onorario'] or 0))
                acconti = c2.number_input("Acconti Ricevuti (€)", value=float(row['Acconti'] or 0))
                c3.metric("Saldo", f"{onorario - acconti:,.2f} €")
            with t3:
                appunti = st.text_area("Appunti di cantiere:", value=row['Note'], height=150)
                if st.button("🤖 GENERA VERBALE"):
                    res = genera_verbale_ai(appunti, api_key)
                    st.session_state.verbale_generato = res
                if "verbale_generato" in st.session_state:
                    appunti = st.text_area("Verbale Finale:", value=st.session_state.verbale_generato, height=300)
                impresa = st.text_input("Impresa Esecutrice", value=row['Impresa'])
            with t4:
                c_durc = st.checkbox("DURC", value=(row['chk_durc']=="1"))
                c_cont = st.checkbox("Contratti", value=(row['chk_contratti']=="1"))
                c_urb = st.checkbox("Pratica Urbanistica", value=(row['chk_urbanistica']=="1"))
                c_fine = st.checkbox("Fine Lavori", value=(row['chk_finelavori']=="1"))
                c_acca = st.checkbox("Accatastamento", value=(row['chk_accatastamento']=="1"))
            if st.button("💾 SALVA"):
                idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                df_can.loc[idx, ['Progresso', 'Stato', 'Onorario', 'Acconti', 'Impresa', 'Note']] = [str(prog), nuovo_stato, str(onorario), str(acconti), impresa, appunti]
                df_can.loc[idx, ['chk_durc', 'chk_contratti', 'chk_urbanistica', 'chk_finelavori', 'chk_accatastamento']] = ["1" if x else "0" for x in [c_durc, c_cont, c_urb, c_fine, c_acca]]
                salva_db(df_can, DB_CAN); st.success("Salvato!"); st.rerun()
        else:
            st.header("🚧 Direzione Lavori")
            if st.button("⬅️ PLANCIA"): st.session_state.sotto_menu = None; st.rerun()
            with st.expander("➕ NUOVO CANTIERE"):
                with st.form("n_c"):
                    cli = st.selectbox("Cliente", [""] + df_ana["Cliente"].tolist())
                    ind = st.text_input("Indirizzo")
                    if st.form_submit_button("CREA"):
                        new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": cli, "Indirizzo": ind, "Stato": "Iniziale", "Progresso": "0"}
                        df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                        salva_db(df_can, DB_CAN); st.rerun()
            for _, r in df_can.iterrows():
                st.markdown(f'<div class="cantiere-card"><b>{r["Cliente"]}</b> - {r["Indirizzo"]}</div>', unsafe_allow_html=True)
                if st.button(f"📂 APRI", key=f"op_{r['id_cantiere']}"):
                    st.session_state.cantiere_aperto = r['id_cantiere']; st.rerun()

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
            if st.button("📋\nPRATICHE\nCILA/SCIA", key="main_pra", use_container_width=True): st.toast("Pratiche")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", key="main_mill", use_container_width=True): st.toast("Millesimi")
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", key="main_ape", use_container_width=True): st.toast("APE")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", key="main_alt", use_container_width=True): st.toast("Altro")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenze")
    st.dataframe(df_ana[["Cliente", "Pratica", "Scadenza"]], use_container_width=True, hide_index=True)import streamlit as st
import pandas as pd
import os
import openai

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
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
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .cantiere-card { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #e2e8f0; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

def genera_verbale_ai(testo_appunti, api_key):
    if not api_key:
        return "Errore: Inserisci la API Key nella sidebar per usare l'AI."
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei l'Architetto Silvia Cubeddu. Trasforma gli appunti di cantiere in un verbale di sopralluogo professionale, formale e strutturato."},
                {"role": "user", "content": f"Trasforma questi appunti in un verbale formale: {testo_appunti}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore AI: {str(e)}"

DB_ANA = "database_archiflow.csv"
DB_CAN = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Progresso", "Onorario", "Acconti", "Impresa", "Note", 
           "chk_durc", "chk_contratti", "chk_urbanistica", "chk_finelavori", "chk_accatastamento"]

def carica_db(file, colonne):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, dtype=str).fillna("")
            for col in colonne:
                if col not in df.columns: df[col] = "0" if "chk_" in col or col in ["Progresso", "Onorario", "Acconti"] else ""
            return df[colonne]
        except: return pd.DataFrame(columns=colonne)
    return pd.DataFrame(columns=colonne)

def salva_db(df, file):
    df.to_csv(file, index=False)

df_ana = carica_db(DB_ANA, COL_ANA)
df_can = carica_db(DB_CAN, COL_CAN)

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

if menu == "HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.subheader("Database Clienti")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "aggiungi"; st.session_state.ana_sel = None; st.rerun()
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        df_v = df_ana[["id", "Cliente"]].copy(); df_v.insert(0, "Sel.", False)
        ed = st.data_editor(df_v, hide_index=True, use_container_width=True, key="ana_ed")
        sel = ed[ed["Sel."] == True]["id"].tolist()
        if sel and st.button("📂 APRI SCHEDA"):
            st.session_state.modo_ana = "modifica"; st.session_state.ana_sel = sel[-1]; st.rerun()

    with col_r:
        if st.session_state.get("modo_ana"):
            with st.form("form_ana"):
                id_a = st.session_state.ana_sel
                d = df_ana[df_ana['id'] == id_a].iloc[0].to_dict() if id_a else {c: "" for c in COL_ANA}
                new_d = {"id": id_a if id_a else str(len(df_ana)+1)}
                c1, c2 = st.columns(2)
                for i, c in enumerate(COL_ANA[1:]):
                    new_d[c] = (c1 if i%2==0 else c2).text_input(c, value=str(d.get(c, "")))
                if st.form_submit_button("SALVA"):
                    if not id_a: df_ana = pd.concat([df_ana, pd.DataFrame([new_d])], ignore_index=True)
                    else: df_ana.loc[df_ana['id'] == id_a] = list(new_d.values())
                    salva_db(df_ana, DB_ANA); st.rerun()

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        if st.session_state.get("cantiere_aperto"):
            id_c = st.session_state.cantiere_aperto
            row = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.header(f"🏗️ Cantiere: {row['Cliente']}")
            if st.button("⬅️ TORNA"): st.session_state.cantiere_aperto = None; st.rerun()
            t1, t2, t3, t4 = st.tabs(["📊 STATO", "💰 ECONOMIA", "🎙️ VOCALE & AI", "📋 CHECKLIST"])
            with t1:
                prog = st.slider("Avanzamento (%)", 0, 100, int(row['Progresso']))
                st.progress(prog / 100)
                nuovo_stato = st.selectbox("Stato", ["Iniziale", "In Corso", "Sospeso", "Ultimato"], index=0)
            with t2:
                c1, c2, c3 = st.columns(3)
                onorario = c1.number_input("Onorario Totale (€)", value=float(row['Onorario'] or 0))
                acconti = c2.number_input("Acconti Ricevuti (€)", value=float(row['Acconti'] or 0))
                c3.metric("Saldo", f"{onorario - acconti:,.2f} €")
            with t3:
                appunti = st.text_area("Appunti di cantiere:", value=row['Note'], height=150)
                if st.button("🤖 GENERA VERBALE"):
                    res = genera_verbale_ai(appunti, api_key)
                    st.session_state.verbale_generato = res
                if "verbale_generato" in st.session_state:
                    appunti = st.text_area("Verbale Finale:", value=st.session_state.verbale_generato, height=300)
                impresa = st.text_input("Impresa Esecutrice", value=row['Impresa'])
            with t4:
                c_durc = st.checkbox("DURC", value=(row['chk_durc']=="1"))
                c_cont = st.checkbox("Contratti", value=(row['chk_contratti']=="1"))
                c_urb = st.checkbox("Pratica Urbanistica", value=(row['chk_urbanistica']=="1"))
                c_fine = st.checkbox("Fine Lavori", value=(row['chk_finelavori']=="1"))
                c_acca = st.checkbox("Accatastamento", value=(row['chk_accatastamento']=="1"))
            if st.button("💾 SALVA"):
                idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                df_can.loc[idx, ['Progresso', 'Stato', 'Onorario', 'Acconti', 'Impresa', 'Note']] = [str(prog), nuovo_stato, str(onorario), str(acconti), impresa, appunti]
                df_can.loc[idx, ['chk_durc', 'chk_contratti', 'chk_urbanistica', 'chk_finelavori', 'chk_accatastamento']] = ["1" if x else "0" for x in [c_durc, c_cont, c_urb, c_fine, c_acca]]
                salva_db(df_can, DB_CAN); st.success("Salvato!"); st.rerun()
        else:
            st.header("🚧 Direzione Lavori")
            if st.button("⬅️ PLANCIA"): st.session_state.sotto_menu = None; st.rerun()
            with st.expander("➕ NUOVO CANTIERE"):
                with st.form("n_c"):
                    cli = st.selectbox("Cliente", [""] + df_ana["Cliente"].tolist())
                    ind = st.text_input("Indirizzo")
                    if st.form_submit_button("CREA"):
                        new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": cli, "Indirizzo": ind, "Stato": "Iniziale", "Progresso": "0"}
                        df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                        salva_db(df_can, DB_CAN); st.rerun()
            for _, r in df_can.iterrows():
                st.markdown(f'<div class="cantiere-card"><b>{r["Cliente"]}</b> - {r["Indirizzo"]}</div>', unsafe_allow_html=True)
                if st.button(f"📂 APRI", key=f"op_{r['id_cantiere']}"):
                    st.session_state.cantiere_aperto = r['id_cantiere']; st.rerun()

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
            if st.button("📋\nPRATICHE\nCILA/SCIA", key="main_pra", use_container_width=True): st.toast("Pratiche")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", key="main_mill", use_container_width=True): st.toast("Millesimi")
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", key="main_ape", use_container_width=True): st.toast("APE")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", key="main_alt", use_container_width=True): st.toast("Altro")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenze")
    st.dataframe(df_ana[["Cliente", "Pratica", "Scadenza"]], use_container_width=True, hide_index=True)
    
