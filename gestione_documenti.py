import streamlit as st
import pandas as pd
import json
from gestione_documenti import inizializza_documenti

def mostra_anagrafica(conn):
    st.markdown("""
        <style>
        div[data-testid="stColumn"] { display: flex !important; align-items: flex-end !important; }
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important; margin-bottom: -10px !important;
        }
        .header-btn > div > button { height: 45px !important; font-weight: 900 !important; border-radius: 10px !important; }
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        .btn-aggiorna > div > button { background-color: #457B9D !important; color: white !important; height: 48px !important; font-weight: bold !important; border: none !important; }
        .btn-checklist > div > button { background-color: #f59e0b !important; color: white !important; height: 48px !important; font-weight: 900 !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")
    df = pd.read_sql("SELECT * FROM lavori", conn)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("Cerca", placeholder="Filtra clienti...", label_visibility="collapsed")
    with c2:
        st.markdown('<div class="header-btn btn-new">', unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            conn.execute("INSERT INTO lavori (Cliente, Pratica, Stato, docs_json) VALUES ('', 'Altro', 'Da fare', '{}')")
            conn.commit(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="header-btn btn-del">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v]
            if selezionati:
                ph = ','.join(['?'] * len(selezionati))
                conn.execute(f"DELETE FROM lavori WHERE id IN ({ph})", selezionati)
                conn.commit(); st.session_state.cliente_sel_id = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    col_lista, col_scheda = st.columns([1.2, 2])
    with col_lista:
        df_filt = df[df['Cliente'].str.contains(search, case=False)] if search else df
        for _, r in df_filt.iterrows():
            cl1, cl2 = st.columns([0.15, 0.85])
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if cl2.button(f"👤 {r['Cliente'] or 'Nuovo'}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = r['id']; st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            r = pd.read_sql("SELECT * FROM lavori WHERE id = ?", conn, params=(sel_id,)).iloc[0]
            st.subheader(f"📑 {r['Cliente'] or 'Dati Pratica'}")
            
            u_cli = st.text_input("Ragione Sociale", r['Cliente'])
            c_an1, c_an2, c_an3 = st.columns([1.5, 1, 1.5])
            
            # TUTTE LE PRATICHE
            lista_p = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "APE / Legge 10", "Altro"]
            u_pra = c_an1.selectbox("Pratica", lista_p, index=lista_p.index(r['Pratica']) if r['Pratica'] in lista_p else 14)
            u_sta = c_an2.selectbox("Stato", ["Da fare", "In corso", "Annullata", "Conclusa", "Sospesa"], index=0)
            u_sca = c_an3.text_input("Scadenza", r.get('Scadenza', ''))
            u_note = st.text_area("Note", r.get('Note', ''), height=100)

            st.write("---")
            b_agg, b_chk = st.columns(2)
            with b_agg:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("💾 AGGIORNA DATI", use_container_width=True):
                    conn.execute("UPDATE lavori SET Cliente=?, Pratica=?, Stato=?, Scadenza=?, Note=? WHERE id=?", (u_cli, u_pra, u_sta, u_sca, u_note, sel_id))
                    conn.commit(); st.success("Salvato!"); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with b_chk:
                st.markdown('<div class="btn-checklist">', unsafe_allow_html=True)
                if st.button(f"📋 CHECKLIST {u_pra.upper()}", use_container_width=True):
                    mostra_checklist_dialog(conn, sel_id, u_pra, r['docs_json'])
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente.")

@st.dialog("📋 Gestione Documenti")
def mostra_checklist_dialog(conn, sel_id, pratica, docs_json):
    docs = inizializza_documenti(docs_json, pratica)
    nuovi_stati = {}
    for d, s in docs.items():
        cx1, cx2 = st.columns([3, 2])
        cx1.markdown(f"**{d}**")
        opz = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
        idx = opz.index(s) if s in opz else 0
        nuovi_stati[d] = cx2.selectbox(f"S_{d}", opz, index=idx, key=f"m_{d}", label_visibility="collapsed")
    if st.button("💾 SALVA E CHIUDI", use_container_width=True):
        conn.execute("UPDATE lavori SET docs_json = ? WHERE id = ?", (json.dumps(nuovi_stati), sel_id))
        conn.commit(); st.rerun()
