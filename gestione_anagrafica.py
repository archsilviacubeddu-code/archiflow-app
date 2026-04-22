import streamlit as st
import pandas as pd
from gestione_documenti import interfaccia_semafori

def mostra_anagrafica(df, DB_FILE, COLONNE):
    # --- AUTO-PULIZIA RIGHE VUOTE ---
    # Se ci sono righe senza nome cliente che non sono quella attualmente selezionata, le eliminiamo
    idx_attuale = st.session_state.get('cliente_sel')
    
    # Identifichiamo le righe "fantasma" (Nome vuoto e non sono quelle su cui stiamo lavorando)
    mask_vuoti = (df['Cliente'] == "") | (df['Cliente'].isna())
    if idx_attuale is not None:
        # Non cancelliamo la riga che l'utente ha appena creato e sta guardando
        mask_vuoti.iloc[idx_attuale] = False
    
    if mask_vuoti.any():
        df = df[~mask_vuoti].reset_index(drop=True)
        df.to_csv(DB_FILE, index=False)
        # Se abbiamo resettato gli indici, dobbiamo aggiornare la selezione
        if idx_attuale is not None:
            st.session_state.cliente_sel = None # Reset per sicurezza dopo la pulizia
        st.rerun()

    # CSS Custom
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
            height: 50px !important; font-weight: bold !important; border: none !important;
        }
        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    
    with c2:
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            # Creiamo riga VERAMENTE vuota
            nuova_riga = pd.DataFrame([[nuovo_id, "", "", "", "", "", "", "", "", "Altro", "Da fare", "", "", "{}"]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()
        
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            label_cli = r['Cliente'] if r['Cliente'] != "" else "✨ NUOVA VOCE..."
            if c_btn.button(f"👤 {label_cli}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente'] or 'Nuova Pratica'}")
            
            u_cli = st.text_input("👤 Nome / Ragione Sociale", value=r['Cliente'], placeholder="Scrivi il nome per salvare...")
            u_cf = st.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c3, c4, c5 = st.columns([2, 1, 1.5])
            u_ind = c3.text_input("🏠 Indirizzo", r['Indirizzo'])
            u_cap = c4.text_input("📮 CAP", r['CAP'])
            u_cit = c5.text_input("🏙️ Città", r['Città'])

            st.write("---")
            u_ind_cantiere = st.text_input("📍 Indirizzo Pratica / Cantiere", r['Web'])
            
            c6, c7, c8 = st.columns([1.5, 1, 1.5])
            voci_pratica = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "Altro"]
            default_p = r['Pratica'] if r['Pratica'] in voci_pratica else "Altro"
            u_pra = c6.selectbox("🏗️ Tipo Pratica", voci_pratica, index=voci_pratica.index(default_p))
            u_sta = c7.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], index=0)
            u_sca = c8.text_input("📅 Scadenza", r['Scadenza'])
            
            u_tel = st.text_input("📞 Telefono", r['Telefono'])
            u_mail = st.text_input("📧 Email", r['Email'])
            u_note = st.text_area("📝 Note", r['Note'], height=120)

            st.write("---")
            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            if st.button("🔄 AGGIORNA E CONFERMA", use_container_width=True):
                if u_cli.strip() == "":
                    st.error("Devi inserire un nome cliente per salvare!")
                else:
                    df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, u_ind_cantiere, u_pra, u_sta, u_sca, u_note, r['docs_json']]
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvato!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
