import streamlit as st
import pandas as pd
import json
from gestione_documenti import inizializza_documenti

def mostra_anagrafica(conn):
    # CSS: ALLINEAMENTO TOTALE COATTO
    st.markdown("""
        <style>
        /* Questo blocca i bottoni sulla stessa linea dell'input Cerca */
        [data-testid="column"] {
            display: flex !important;
            align-items: flex-end !important;
        }
        
        /* Sistema l'altezza dei bottoni per pareggiarli all'input */
        .header-btn > div > button {
            height: 42px !important; 
            font-weight: 900 !important;
            border-radius: 10px !important;
            margin-bottom: 0px !important;
        }
        
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { 
            background-color: #fee2e2 !important; color: #ef4444 !important; 
            border: 1px solid #ef4444 !important; 
        }

        /* Bottoni lista a sinistra */
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important;
        }
        
        /* Pulsanti fondo scheda */
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 45px !important; font-weight: bold !important; border: none !important;
        }
        .btn-checklist > div > button {
            background-color: #f59e0b !important; color: white !important;
            height: 45px !important; font-weight: 900 !important; border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")
    df = pd.read_sql("SELECT * FROM lavori", conn)

    # 1. BARRA SUPERIORE: ALLINEAMENTO FISSO
    c_search, c_new, c_del = st.columns([2, 1, 1])
    
    with c_search:
        search = st.text_input("Cerca", placeholder="Filtra clienti...", label_visibility="collapsed")
    
    with c_new:
        st.markdown('<div class="header-btn btn-new">', unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            conn.execute('''INSERT INTO lavori 
                (Cliente, Pratica, Stato, docs_json, Scadenza, CF_PIVA, Indirizzo, CAP, Citta, Telefono, Email, Web, Note) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                ("", "Altro", "Da fare", "{}", "", "", "", "", "", "", "", "", ""))
            conn.commit()
            last_id = pd.read_sql("SELECT last_insert_rowid() as id", conn).iloc[0]['id']
            st.session_state.cliente_sel_id = int(last_id)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_del:
        st.markdown('<div class="header-btn btn-del">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                ph = ','.join(['?'] * len(selezionati))
                conn.execute(f"DELETE FROM lavori WHERE id IN ({ph})", selezionati)
                conn.commit(); st.session_state.cliente_sel_id = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. LAYOUT LISTA E SCHEDA
    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for _, r in df_filt.iterrows():
            cl1, cl2 = st.columns([0.15, 0.85])
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            label = r['Cliente'] if r['Cliente'] else "📝 (Nuova voce)"
            if cl2.button(f"👤 {label}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = r['id']; st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            r = pd.read_sql("SELECT * FROM lavori WHERE id = ?", conn, params=(sel_id,)).iloc[0]
            st.subheader(f"📑 {r['Cliente'] if r['Cliente'] else 'Dati Pratica'}")
            
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("Ragione Sociale", r['Cliente'])
            u_cf = c2.text_input("C.F. / P.IVA", r['CF_PIVA'])
            
            c3, c4, c5 = st.columns([1.5, 1, 1.5])
            lista_p = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "APE / Legge 10", "Altro"]
            u_pra = c3.selectbox("Pratica", lista_p, index=lista_p.index(r['Pratica']) if r['Pratica'] in lista_p else 13)
            u_sta = c4.selectbox("Stato", ["Da fare", "In corso", "Annullata", "Conclusa", "Sospesa"], index=0)
            u_sca = c5.text_input("📅 Scadenza", r['Scadenza'])
            
            u_note = st.text_area("Note", r['Note'], height=80)

            # PULSANTI FONDO SCHEDA
            st.write("---")
            b_agg, b_chk = st.columns(2)
            with b_agg:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("💾 AGGIORNA DATI", use_container_width=True):
                    conn.execute('''UPDATE lavori SET Cliente=?, CF_PIVA=?, Pratica=?, Stato=?, Scadenza=?, Note=? WHERE id=?''', 
                                 (u_cli, u_cf, u_pra, u_sta, u_sca, u_note, sel_id))
                    conn.commit(); st.success("Salvato!"); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with b_chk:
                st.markdown('<div class="btn-checklist">', unsafe_allow_html=True)
                if st.button(f"📋 APRI CHECKLIST {u_pra.upper()}", use_container_width=True):
                    apri_modal_docs(conn, sel_id, u_pra, r['docs_json'])
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente.")

# 3. MODAL DOCUMENTI
@st.dialog("📋 Checklist Documenti")
def apri_modal_docs(conn, sel_id, pratica, docs_json):
    st.write(f"Gestione per: **{pratica}**")
    docs = inizializza_documenti(docs_json, pratica)
    nuovi = {}
    for d, s in docs.items():
        cx1, cx2 = st.columns([3, 2])
        cx1.markdown(f"**{d}**")
        opz = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
        idx = opz.index(s) if s in opz else 0
        nuovi[d] = cx2.selectbox(f"S_{d}", opz, index=idx, key=f"m_{d}", label_visibility="collapsed")
    if st.button("💾 SALVA E CHIUDI", use_container_width=True):
        conn.execute("UPDATE lavori SET docs_json = ? WHERE id = ?", (json.dumps(nuovi), sel_id))
        conn.commit(); st.rerun()
