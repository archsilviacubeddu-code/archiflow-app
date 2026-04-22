import streamlit as st
import pandas as pd
from gestione_documenti import interfaccia_semafori

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 15px !important;
        }
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 45px !important; font-weight: bold !important; border: none !important;
        }
        .btn-cancella-top > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important; height: 45px !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # BARRA COMANDI ALTA
    c1, c2 = st.columns([2, 2])
    with c1:
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "", "", "", "", "", "", "", "", "Altro", "Da fare", "", "", "{}"]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()
    
    with c2:
        st.markdown('<div class="btn-cancella-top">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA SELEZIONATI", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                for k in selezionati: 
                    if f"check_{k}" in st.session_state: del st.session_state[f"check_{k}"]
                st.session_state.cliente_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.2, 0.8])
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            label_cliente = r['Cliente'] if r['Cliente'] != "" else "Nuovo Cliente"
            if c_btn.button(f"👤 {label_cliente}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente'] or 'Nuovo Cliente'}")
            
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("👤 Nome / Ragione Sociale", value=r['Cliente'], placeholder="Inserisci nome...")
            u_cf = c2.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c3, c4, c5 = st.columns([2, 1, 1.5])
            u_ind = c3.text_input("🏠 Indirizzo", r['Indirizzo'])
            u_cap = c4.text_input("📮 CAP", r['CAP'])
            u_cit = c5.text_input("🏙️ Città", r['Città'])

            st.write("---")
            u_ind_cantiere = st.text_input("📍 Indirizzo Pratica / Cantiere", r['Web'])
            
            c6, c7, c8 = st.columns([1.5, 1, 1.5])
            # TUA LISTA PRATICHE INTEGRATA
            lista_pratiche = [
                "Cantiere interni", "Cantiere esterni", "Direzione lavori", 
                "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", 
                "Accertamento di conformità", "Millesimi", "Perizia", 
                "Accesso atti", "Render", "Altro"
            ]
            default_pra = r['Pratica'] if r['Pratica'] in lista_pratiche else "Altro"
            u_pra = c6.selectbox("🏗️ Tipo Pratica", lista_pratiche, index=lista_pratiche.index(default_pra))
            
            u_sta = c7.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], index=0)
            u_sca = c8.text_input("📅 Scadenza", r['Scadenza'], placeholder="gg/mm/aaaa")
            
            c9, c10 = st.columns(2)
            u_tel = c9.text_input("📞 Telefono", r['Telefono'])
            u_mail = c10.text_input("📧 Email", r['Email'])
            
            u_note = st.text_area("📝 Note", r['Note'], height=120)

            # --- SEMAFORI DOCUMENTI (INTEGRATI) ---
            st.write("---")
            interfaccia_semafori(u_pra, df, idx)
            
            st.write("---")
            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            if st.button("🔄 AGGIORNA E SALVA", use_container_width=True):
                df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, u_ind_cantiere, u_pra, u_sta, u_sca, u_note, df.at[idx, 'docs_json']]
                df.to_csv(DB_FILE, index=False)
                st.success("Dati e Documenti Salvati!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
