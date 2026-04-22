import streamlit as st
import pandas as pd
import json
from gestione_documenti import inizializza_documenti

def mostra_anagrafica(conn):
    # CSS per bottoni e stile
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important;
            margin-bottom: -10px !important;
        }
        .header-btn > div > button { height: 45px !important; font-weight: 900 !important; border-radius: 10px !important; }
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        .btn-aggiorna > div > button { background-color: #457B9D !important; color: white !important; height: 45px !important; font-weight: bold !important; }
        .btn-checklist > div > button { background-color: #f59e0b !important; color: white !important; height: 45px !important; font-weight: 900 !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")
    df = pd.read_sql("SELECT * FROM lavori", conn)

    # 1. BARRA SUPERIORE
    c_search, c_new, c_del = st.columns([2, 1, 1])
    with c_search:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra...", label_visibility="collapsed")
    
    with c_new:
        st.markdown('<div class="header-btn btn-new">', unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            conn.execute('''INSERT INTO lavori (Cliente, Pratica, Stato, docs_json, Scadenza, CF_PIVA, Indirizzo, CAP, Citta, Telefono, Email, Web, Note) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', ("", "Altro", "Da fare", "{}", "", "", "", "", "", "", "", "", ""))
            conn.commit(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_del:
        st.markdown('<div class="header-btn btn-del">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                conn.execute(f"DELETE FROM lavori WHERE id IN ({','.join(['?']*len(selezionati))})", selezionati)
                conn.commit(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. LISTA E SCHEDA ANAGRAFICA
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        df_filt = df[df['Cliente'].str.contains(search, case=False)] if search else df
        for _, r in df_filt.iterrows():
            cl1, cl2 = st.columns([0.15, 0.85])
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if cl2.button(f"👤 {r['Cliente'] if r['Cliente'] else '📝 Vuoto'}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = r['id']; st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            r = pd.read_sql("SELECT * FROM lavori WHERE id = ?", conn, params=(sel_id,)).iloc[0]
            
            st.subheader(f"📑 Dati Anagrafici: {r['Cliente']}")
            u_cli = st.text_input("Ragione Sociale", r['Cliente'])
            
            c1, c2 = st.columns([1.5, 1])
            lista_pra = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "APE / Legge 10", "Altro"]
            u_pra = c1.selectbox("Pratica", lista_pra, index=lista_pra.index(r['Pratica']) if r['Pratica'] in lista_pra else 14)
            u_sta = c2.selectbox("Stato", ["Da fare", "In corso", "Annullata", "Conclusa", "Sospesa"], index=0)
            
            # --- IL TASTO CHE APRE LA SCHEDA DOCUMENTI SEPARATA ---
            st.write("")
            st.markdown('<div class="btn-checklist">', unsafe_allow_html=True)
            if st.button(f"📋 APRI CHECKLIST {u_pra.upper()}", use_container_width=True):
                apri_modal_documenti(conn, sel_id, u_pra, r['docs_json'])
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("")

            with st.expander("Altri Dettagli"):
                u_cf = st.text_input("C.F. / P.IVA", r['CF_PIVA'])
                u_sca = st.text_input("Scadenza", r['Scadenza'])
                u_ind = st.text_input("Indirizzo", r['Indirizzo'])
                u_note = st.text_area("Note", r['Note'])

            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            if st.button("🔄 AGGIORNA ANAGRAFICA", use_container_width=True):
                conn.execute('''UPDATE lavori SET Cliente=?, Pratica=?, Stato=?, CF_PIVA=?, Indirizzo=?, Scadenza=?, Note=? WHERE id=?''', 
                             (u_cli, u_pra, u_sta, u_cf, u_ind, u_sca, u_note, sel_id))
                conn.commit(); st.success("Anagrafica salvata!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# 3. FUNZIONE PER LA FINESTRA SEPARATA (MODAL)
@st.dialog("📋 Checklist Documenti")
def apri_modal_documenti(conn, sel_id, pratica, docs_json):
    st.write(f"Gestione documenti per: **{pratica}**")
    docs = inizializza_documenti(docs_json, pratica)
    nuovi_stati = {}
    
    for doc, stato in docs.items():
        c1, c2 = st.columns([3, 2])
        c1.markdown(f"**{doc}**")
        opzioni = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
        def_idx = opzioni.index(stato) if stato in opzioni else 0
        nuovi_stati[doc] = c2.selectbox(f"S_{doc}", opzioni, index=def_idx, key=f"mod_{doc}", label_visibility="collapsed")
    
    st.divider()
    if st.button("💾 SALVA E CHIUDI", use_container_width=True):
        conn.execute("UPDATE lavori SET docs_json = ? WHERE id = ?", (json.dumps(nuovi_stati), sel_id))
        conn.commit()
        st.rerun()
