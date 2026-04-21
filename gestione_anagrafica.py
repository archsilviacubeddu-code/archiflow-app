import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COL_ANAGRAFICA):
    # CSS per rimettere a posto i colori e i bordi della scheda
    st.markdown("""
        <style>
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: white !important;
            border: 1px solid #cbd5e1 !important;
            color: #1e293b !important;
            border-radius: 8px !important;
        }
        .scheda-piena {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        .label-scheda {
            font-weight: bold;
            color: #475569;
            margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📇 Gestione Anagrafica")

    # BARRA SUPERIORE PULITA
    c1, c2 = st.columns([4, 1])
    with c1:
        search = st.text_input("🔍 Cerca per nome o pratica...", placeholder="Inserisci il nome del cliente...")
    with c2:
        st.write("##") # Spazio per allineare il tasto
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "", "Attivo", "", ""]], columns=COL_ANAGRAFICA)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    df_filtrato = df[df['Cliente'].str.contains(search, case=False)] if search else df
    st.divider()

    # LOGICA SCHEDA APERTA
    if st.session_state.get("cliente_selezionato") is not None:
        idx = st.session_state.cliente_selezionato
        r = df.loc[idx]
        
        with st.container():
            st.markdown(f"### 📂 Scheda Dettagliata: {r['Cliente']}")
            
            # Griglia organizzata come un vero modulo professionale
            col1, col2 = st.columns(2)
            u_cli = col1.text_input("Ragione Sociale / Nome", r['Cliente'])
            u_cf = col2.text_input("Codice Fiscale / P.IVA", r['C.F. / P.IVA'])
            
            col3, col4, col5 = st.columns([2, 1, 1])
            u_ind = col3.text_input("Indirizzo", r['Indirizzo'])
            u_cap = col4.text_input("CAP", r['CAP'])
            u_cit = col5.text_input("Città", r['Città'])
            
            col6, col7 = st.columns(2)
            u_tel = col6.text_input("Telefono / Mobile", r['Telefono'])
            u_mail = col7.text_input("Email Professionale", r['Email'])
            
            col8, col9, col10 = st.columns(3)
            u_pra = col8.text_input("Tipo Pratica", r['Pratica'])
            u_sta = col9.selectbox("Stato Pratica", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1)
            u_sca = col10.text_input("Scadenza / Termini", r['Scadenza'])
            
            u_note = st.text_area("Note Interne", r['Note'], height=100)

            # TASTI AZIONE COLORATI
            st.write("##")
            b1, b2, b3 = st.columns(3)
            
            if b1.button("💾 AGGIORNA E SALVA", use_container_width=True, type="primary"):
                df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, r['Web'], u_pra, u_sta, u_sca, u_note]
                df.to_csv(DB_FILE, index=False)
                st.success("Dati salvati!")
                st.rerun()
                
            if b2.button("🗑️ ELIMINA CLIENTE", use_container_width=True):
                df = df.drop(idx)
                df.to_csv(DB_FILE, index=False)
                st.session_state.cliente_selezionato = None
                st.rerun()
                
            if b3.button("❌ CHIUDI", use_container_width=True):
                st.session_state.cliente_selezionato = None
                st.rerun()
        st.divider()

    # LISTA CLIENTI SEMPLICE (BOTTONI LARGHI)
    st.write("### Seleziona un cliente per visualizzarne i dettagli:")
    for i, r in df_filtrato.iterrows():
        # Creiamo un bottone largo che sembra una riga di tabella
        if st.button(f"👤 {r['Cliente']} ——— 🛠️ {r['Pratica']} ——— 📍 {r['Indirizzo']}", key=f"list_{i}", use_container_width=True):
            st.session_state.cliente_selezionato = i
            st.rerun()
