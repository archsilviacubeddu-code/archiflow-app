import streamlit as st
import pandas as pd

def mostra_anagrafica(conn):
    # CSS: Ripristino bottoni piccoli, lista pulita e stile originale
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important;
            margin-bottom: -10px !important;
        }
        /* Bottoni AGGIUNGI e CANCELLA allineati e uguali */
        .header-btn > div > button {
            height: 45px !important; font-weight: 900 !important;
            border-radius: 10px !important;
        }
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 45px !important; font-weight: bold !important; border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # Dati dal Database
    df = pd.read_sql("SELECT * FROM lavori", conn)

    # 1. BARRA SUPERIORE ALLINEATA
    c_search, c_new, c_del = st.columns([2, 1, 1])
    
    with c_search:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra...", label_visibility="collapsed")
    
    with c_new:
        st.markdown('<div class="header-btn btn-new">', unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            conn.execute('''INSERT INTO lavori 
                (Cliente, Pratica, Stato, docs_json, Scadenza, CF_PIVA, Indirizzo, CAP, Citta, Telefono, Email, Web, Note) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                ("NUOVO CLIENTE", "Altro", "Da fare", "{}", "", "", "", "", "", "", "", "", ""))
            conn.commit()
            st.session_state.cliente_sel_id = None # Pulisce la scheda quando aggiungi
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_del:
        st.markdown('<div class="header-btn btn-del">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                placeholder = ','.join(['?'] * len(selezionati))
                conn.execute(f"DELETE FROM lavori WHERE id IN ({placeholder})", selezionati)
                conn.commit()
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel_id = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Filtro
    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df

    st.divider()

    # 2. LISTA E SCHEDA
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for _, r in df_filt.iterrows():
            cl1, cl2 = st.columns([0.15, 0.85])
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if cl2.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = r['id']
                st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            res = pd.read_sql("SELECT * FROM lavori WHERE id = ?", conn, params=(sel_id,))
            if not res.empty:
                r = res.iloc[0]
                st.subheader(f"📑 {r['Cliente']}")
                
                c1, c2 = st.columns(2)
                u_cli = c1.text_input("Ragione Sociale", r['Cliente'])
                u_cf = c2.text_input("C.F. / P.IVA", r['CF_PIVA'])
                
                c3, c4, c5 = st.columns([2, 1, 1.5])
                u_ind = c3.text_input("Indirizzo", r['Indirizzo'])
                u_cap = c4.text_input("CAP", r['CAP'])
                u_cit = c5.text_input("Città", r['Citta'])

                st.write("---")
                u_web = st.text_input("📍 Indirizzo Cantiere", r['Web'])
                
                c6, c7, c8 = st.columns([1.5, 1, 1.5])
                
                # RIPRISTINO LISTA PRATICHE COMPLETA
                lista_pratiche = [
                    "Cantiere interni", "Cantiere esterni", "Direzione lavori", 
                    "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", 
                    "Accertamento di conformità", "Millesimi", "Perizia", 
                    "Accesso atti", "Render", "Altro"
                ]
                default_p = r['Pratica'] if r['Pratica'] in lista_pratiche else "Altro"
                u_pra = c6.selectbox("Pratica", lista_pratiche, index=lista_pratiche.index(default_p))
                
                u_sta = c7.selectbox("Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], index=0)
                u_sca = c8.text_input("Scadenza", r['Scadenza'])

                c9, c10 = st.columns(2)
                u_tel = c9.text_input("Telefono", r['Telefono'])
                u_mail = c10.text_input("Email", r['Email'])
                
                u_note = st.text_area("Note", r['Note'], height=100)

                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("🔄 AGGIORNA DATI", use_container_width=True):
                    conn.execute('''UPDATE lavori SET Cliente=?, CF_PIVA=?, Indirizzo=?, CAP=?, Citta=?, 
                                    Telefono=?, Email=?, Web=?, Pratica=?, Stato=?, Scadenza=?, Note=? WHERE id=?''', 
                                 (u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, u_web, u_pra, u_sta, u_sca, u_note, sel_id))
                    conn.commit()
                    st.success("Salvato!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente o aggiungine uno nuovo.")
