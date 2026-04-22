import streamlit as st
import pandas as pd

def mostra_anagrafica(conn):
    # CSS Custom - Il tuo stile originale intatto
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 15px !important;
        }
        div.stButton > button[key="btn_new"], .btn-del-massivo > div > button {
            height: 45px !important; font-weight: bold !important; margin-top: 5px !important;
        }
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 45px !important; font-weight: bold !important; border: none !important;
        }
        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
        }
        .btn-elimina-singolo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important; height: 45px !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # Caricamento dati dal database SQL
    df = pd.read_sql("SELECT * FROM lavori", conn)

    # 1. RICERCA E COMANDI
    c1, c2 = st.columns([3, 1])
    
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    
    with c2:
        # AGGIUNGI NUOVO CLIENTE
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            conn.execute('''INSERT INTO lavori 
                (Cliente, Pratica, Stato, docs_json, Scadenza, CF_PIVA, Indirizzo, CAP, Citta, Telefono, Email, Web, Note) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                ("Nuovo Cliente", "Altro", "Da fare", "{}", "", "", "", "", "", "", "", "", ""))
            conn.commit()
            st.rerun()
        
        # CANCELLA MASSIVO (basato sui checkbox selezionati)
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                for sel_id in selezionati:
                    conn.execute("DELETE FROM lavori WHERE id = ?", (sel_id,))
                conn.commit()
                # Pulisce i checkbox
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel_id = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Filtro ricerca
    if search:
        df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
    else:
        df_filt = df

    st.divider()

    # 2. LAYOUT LISTA E SCHEDA DETTAGLIO
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = r['id']
                st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            # Recupera i dati aggiornati della riga selezionata
            r_query = pd.read_sql("SELECT * FROM lavori WHERE id = ?", conn, params=(sel_id,))
            if not r_query.empty:
                r = r_query.iloc[0]
                st.subheader(f"📑 Scheda: {r['Cliente']}")
                
                # DATI ANAGRAFICI
                c1, c2 = st.columns(2)
                u_cli = c1.text_input("👤 Nome / Ragione Sociale", r['Cliente'])
                u_cf = c2.text_input("🆔 C.F. / P.IVA", r['CF_PIVA'])
                
                c3, c4, c5 = st.columns([2, 1, 1.5])
                u_ind = c3.text_input("🏠 Indirizzo", r['Indirizzo'])
                u_cap = c4.text_input("📮 CAP", r['CAP'])
                u_cit = c5.text_input("🏙️ Città", r['Citta'])

                st.write("---")
                u_ind_cantiere = st.text_input("📍 Indirizzo Pratica / Cantiere", r['Web'])
                
                c6, c7, c8 = st.columns([1.5, 1, 1.5])
                lista_pratiche = [
                    "Cantiere interni", "Cantiere esterni", "Direzione lavori", 
                    "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", 
                    "Accertamento di conformità", "Millesimi", "Perizia", 
                    "Accesso atti", "Render", "Altro"
                ]
                default_p = r['Pratica'] if r['Pratica'] in lista_pratiche else "Altro"
                u_pra = c6.selectbox("🏗️ Tipo Pratica", lista_pratiche, index=lista_pratiche.index(default_p))
                
                lista_stati = ["Da fare", "In corso", "Chiusa", "Annullata"]
                default_s = r['Stato'] if r['Stato'] in lista_stati else "Da fare"
                u_sta = c7.selectbox("🚦 Stato", lista_stati, index=lista_stati.index(default_s))
                u_sca = c8.text_input("📅 Scadenza", r['Scadenza'])
                
                c9, c10 = st.columns(2)
                u_tel = c9.text_input("📞 Telefono", r['Telefono'])
                u_mail = c10.text_input("📧 Email", r['Email'])
                
                u_note = st.text_area("📝 Note", r['Note'], height=120)

                st.write("---")
                b_agg_col, b_del_col = st.columns(2)
                
                with b_agg_col:
                    st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                    if st.button("🔄 AGGIORNA", use_container_width=True):
                        conn.execute('''UPDATE lavori SET 
                            Cliente=?, CF_PIVA=?, Indirizzo=?, CAP=?, Citta=?, 
                            Telefono=?, Email=?, Web=?, Pratica=?, Stato=?, 
                            Scadenza=?, Note=? WHERE id=?''', 
                            (u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, 
                             u_ind_cantiere, u_pra, u_sta, u_sca, u_note, sel_id))
                        conn.commit()
                        st.success("Salvato!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with b_del_col:
                    st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                    if st.button("🗑️ ELIMINA", use_container_width=True):
                        conn.execute("DELETE FROM lavori WHERE id = ?", (sel_id,))
                        conn.commit()
                        st.session_state.cliente_sel_id = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
