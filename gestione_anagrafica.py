import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COLONNE):
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

    # 1. RICERCA E COMANDI (Allineamento come richiesto)
    c1, c2 = st.columns([3, 1])
    
    with c1:
        # Il cerca esattamente dove stava prima
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    
    with c2:
        # Aggiungi Cliente
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            # Creazione riga con tutti i campi necessari per evitare errori
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Altro", "Da fare", "", "", "{}"]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()
        
        # Cancella Massivo SOTTO Aggiungi
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                # Pulizia checkbox in session_state
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Filtro ricerca
    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    # 2. LAYOUT LISTA (Checkbox + Nome) E SCHEDA DETTAGLIO
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            # Checkbox per selezione multipla
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            # DATI ANAGRAFICI
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("👤 Nome / Ragione Sociale", r['Cliente'])
            u_cf = c2.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c3, c4, c5 = st.columns([2, 1, 1.5])
            u_ind = c3.text_input("🏠 Indirizzo", r['Indirizzo'])
            u_cap = c4.text_input("📮 CAP", r.get('CAP', ''))
            u_cit = c5.text_input("🏙️ Città", r.get('Città', ''))

            st.write("---")
            # INDIRIZZO CANTIERE
            u_ind_cantiere = st.text_input("📍 Indirizzo Pratica / Cantiere", r.get('Web', ''))
            
            c6, c7, c8 = st.columns([1.5, 1, 1.5])
            # MENU PRATICA CON LA TUA LISTA DEFINITIVA
            lista_pratiche = [
                "Cantiere interni", "Cantiere esterni", "Direzione lavori", 
                "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", 
                "Accertamento di conformità", "Millesimi", "Perizia", 
                "Accesso atti", "Render", "Altro"
            ]
            default_p = r['Pratica'] if r['Pratica'] in lista_pratiche else "Altro"
            u_pra = c6.selectbox("🏗️ Tipo Pratica", lista_pratiche, index=lista_pratiche.index(default_p))
            
            u_sta = c7.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], index=0)
            u_sca = c8.text_input("📅 Scadenza", r['Scadenza'])
            
            c9, c10 = st.columns(2)
            u_tel = c9.text_input("📞 Telefono", r['Telefono'])
            u_mail = c10.text_input("📧 Email", r['Email'])
            
            u_note = st.text_area("📝 Note", r['Note'], height=120)

            st.write("---")
            # TASTI SALVA ED ELIMINA SINGOLO
            b_agg_col, b_del_col = st.columns(2)
            
            with b_agg_col:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("🔄 AGGIORNA", use_container_width=True):
                    # Salvataggio di tutti i campi, incluso l'hidden docs_json
                    df.loc[idx] = [
                        r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, 
                        u_tel, u_mail, u_ind_cantiere, u_pra, u_sta, 
                        u_sca, u_note, r.get('docs_json', '{}')
                    ]
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvato!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with b_del_col:
                st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                if st.button("🗑️ ELIMINA", use_container_width=True):
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.session_state.cliente_sel = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
