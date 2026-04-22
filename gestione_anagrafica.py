import streamlit as st
import pandas as pd
import json
from gestione_documenti import inizializza_documenti

def mostra_anagrafica(conn):
    # CSS: ALLINEAMENTO TOTALE BARRA E STILE SCHEDE
    st.markdown("""
        <style>
        /* Allineamento barra superiore (Cerca, Aggiungi, Cancella) */
        div[data-testid="stColumn"] {
            display: flex !important;
            align-items: flex-end !important;
        }
        
        /* Bottoni lista a sinistra */
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important;
            margin-bottom: -10px !important;
        }
        
        /* Bottoni testata */
        .header-btn > div > button {
            height: 42px !important; font-weight: 900 !important;
            border-radius: 10px !important;
        }
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        
        /* Pulsante Salva in fondo */
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 50px !important; font-weight: bold !important; border: none !important;
            margin-top: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")
    df = pd.read_sql("SELECT * FROM lavori", conn)

    # 1. BARRA SUPERIORE ALLINEATA
    c_search, c_new, c_del = st.columns([2, 1, 1])
    with c_search:
        search = st.text_input("Cerca", placeholder="Filtra...", label_visibility="collapsed")
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
                ph = ','.join(['?'] * len(selezionati))
                conn.execute(f"DELETE FROM lavori WHERE id IN ({ph})", selezionati)
                conn.commit(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. LISTA E SCHEDA A DOPPIA TAB
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
            
            # --- CREAZIONE DELLE SCHEDE (TABS) ---
            tab1, tab2 = st.tabs(["📝 DATI ANAGRAFICI", "🚦 CHECKLIST DOCUMENTI"])

            with tab1:
                u_cli = st.text_input("Ragione Sociale", r['Cliente'])
                c1, c2 = st.columns([1.5, 1])
                lista_pra = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "APE / Legge 10", "Altro"]
                u_pra = c1.selectbox("Pratica", lista_pra, index=lista_pra.index(r['Pratica']) if r['Pratica'] in lista_pra else 14)
                u_sta = c2.selectbox("Stato", ["Da fare", "In corso", "Annullata", "Conclusa", "Sospesa"], index=0)
                
                c3, c4 = st.columns(2)
                u_cf = c3.text_input("C.F. / P.IVA", r['CF_PIVA'])
                u_sca = c4.text_input("Scadenza", r['Scadenza'])
                
                u_ind = st.text_input("Indirizzo", r['Indirizzo'])
                u_web = st.text_input("📍 Indirizzo Cantiere", r['Web'])
                
                c5, c6 = st.columns(2)
                u_tel = c5.text_input("Telefono", r['Telefono'])
                u_mail = c6.text_input("Email", r['Email'])
                u_note = st.text_area("Note", r['Note'], height=100)

            with tab2:
                st.markdown(f"### Checklist: {u_pra}")
                docs = inizializza_documenti(r['docs_json'], u_pra)
                nuovi_stati_docs = {}
                
                for doc, stato in docs.items():
                    cx1, cx2 = st.columns([3, 2])
                    cx1.markdown(f"**{doc}**")
                    opzioni_sem = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
                    def_idx = 0
                    if "🟡" in stato: def_idx = 1
                    elif "🟢" in stato: def_idx = 2
                    nuovi_stati_docs[doc] = cx2.selectbox(f"S_{doc}", opzioni_sem, index=def_idx, key=f"doc_{sel_id}_{doc}", label_visibility="collapsed")

            # BOTTONE UNICO DI SALVATAGGIO
            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            if st.button("🔄 SALVA TUTTO (ANAGRAFICA + DOCUMENTI)", use_container_width=True):
                conn.execute('''UPDATE lavori SET Cliente=?, Pratica=?, Stato=?, docs_json=?, CF_PIVA=?, Indirizzo=?, Web=?, Telefono=?, Email=?, Scadenza=?, Note=? WHERE id=?''', 
                             (u_cli, u_pra, u_sta, json.dumps(nuovi_stati_docs), u_cf, u_ind, u_web, u_tel, u_mail, u_sca, u_note, sel_id))
                conn.commit(); st.success("Dati salvati con successo!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente per iniziare.")
