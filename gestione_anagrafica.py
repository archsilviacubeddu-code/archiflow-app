import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COL_ANAGRAFICA):
    # CSS per bottoni piccoli, allineati a sinistra e professionali
    st.markdown("""
        <style>
        .stTextInput input {
            height: 40px !important;
        }
        /* Bottoni lista clienti: Piccoli e a Sinistra */
        div.stButton > button[key^="list_"] {
            height: 30px !important;
            width: auto !important; /* Non occupa più tutto lo spazio */
            min-width: 300px !important; 
            padding: 0px 15px !important;
            font-size: 13px !important;
            border: 1px solid #e2e8f0 !important;
            color: #475569 !important;
            text-align: left !important;
            background-color: white !important;
            border-radius: 6px !important;
            margin-bottom: -10px !important;
        }
        div.stButton > button[key^="list_"]:hover {
            border-color: #3b82f6 !important;
            color: #3b82f6 !important;
            background-color: #eff6ff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📇 Gestione Anagrafica")

    # BARRA SUPERIORE COMPATTA
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Nome o pratica...", label_visibility="collapsed")
    with c2:
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "", "Attivo", "", ""]], columns=COL_ANAGRAFICA)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    df_filtrato = df[df['Cliente'].str.contains(search, case=False)] if search else df
    st.divider()

    # SCHEDA DETTAGLIATA (Se aperta)
    if st.session_state.get("cliente_selezionato") is not None:
        idx = st.session_state.cliente_selezionato
        r = df.loc[idx]
        
        with st.container():
            st.markdown(f"### 📑 Scheda: {r['Cliente']}")
            col1, col2 = st.columns(2)
            u_cli = col1.text_input("Ragione Sociale", r['Cliente'])
            u_cf = col2.text_input("C.F. / P.IVA", r['C.F. / P.IVA'])
            
            col3, col4, col5 = st.columns([2, 1, 1])
            u_ind = col3.text_input("Indirizzo", r['Indirizzo'])
            u_cap = col4.text_input("CAP", r['CAP'])
            u_cit = col5.text_input("Città", r['Città'])
            
            col6, col7 = st.columns(2)
            u_tel = col6.text_input("Telefono", r['Telefono'])
            u_mail = col7.text_input("Email", r['Email'])
            
            col8, col9, col10 = st.columns(3)
            u_pra = col8.text_input("Pratica", r['Pratica'])
            u_sta = col9.selectbox("Stato", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1)
            u_sca = col10.text_input("Scadenza", r['Scadenza'])
            
            u_note = st.text_area("Note", r['Note'], height=80)

            st.write("##")
            b1, b2, b3 = st.columns(3)
            if b1.button("💾 SALVA", use_container_width=True, type="primary"):
                df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, r['Web'], u_pra, u_sta, u_sca, u_note]
                df.to_csv(DB_FILE, index=False)
                st.rerun()
            if b2.button("🗑️ ELIMINA", use_container_width=True):
                df = df.drop(idx)
                df.to_csv(DB_FILE, index=False)
                st.session_state.cliente_selezionato = None
                st.rerun()
            if b3.button("❌ CHIUDI", use_container_width=True):
                st.session_state.cliente_selezionato = None
                st.rerun()
        st.divider()

    # LISTA CLIENTI COMPATTA A SINISTRA
    st.write("🔍 **Risultati:**")
    for i, r in df_filtrato.iterrows():
        # Il bottone ora è piccolo e non occupa tutta la riga
        if st.button(f"👤 {r['Cliente']} | {r['Pratica']}", key=f"list_{i}"):
            st.session_state.cliente_selezionato = i
            st.rerun()
