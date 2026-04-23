import streamlit as st
import pandas as pd
import json
from sqlalchemy import text
from gestione_documenti import inizializza_documenti

def mostra_lavori(conn):
    # --- CSS: STILE ORIGINALE INTEGRALE ---
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 15px !important;
        }
        .btn-lavoro > div > button {
            height: 8em !important; font-size: 20px !important; border-radius: 20px !important;
            font-weight: 900 !important; color: white !important; margin-bottom: 20px !important; white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }
        
        .btn-aggiorna > div > button { background-color: #457B9D !important; color: white !important; height: 45px !important; font-weight: bold !important; border: none !important; }
        .btn-indietro > div > button { background-color: #1e293b !important; color: white !important; height: 45px !important; }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state: st.session_state.sezione_lavoro = None
    if "lavoro_sel_id" not in st.session_state: st.session_state.lavoro_sel_id = None

    # --- NAVIGAZIONE ---
    if st.session_state.sezione_lavoro:
        render_modulo(st.session_state.sezione_lavoro, conn)
    else:
        st.header("🏗️ Selezione Area di Lavoro")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "DIREZIONE LAVORI"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nURBANISTICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "PRATICHE"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_modulo(sezione, conn):
    # Tasto per tornare indietro
    c_tit, c_back = st.columns([3, 1])
    c_tit.header(f"📂 {sezione}")
    with c_back:
        st.markdown('<div class="btn-indietro">', unsafe_allow_html=True)
        if st.button("⬅️ MENU", use_container_width=True):
            st.session_state.sezione_lavoro = None
            st.session_state.lavoro_sel_id = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CARICAMENTO DATI DA SUPABASE ---
    df = pd.read_sql(text("SELECT * FROM lavori ORDER BY id DESC"), conn)
    
    # --- FILTRO LOGICO SEZIONI ---
    if sezione == "DIREZIONE LAVORI":
        df_f = df[df['Pratica'].str.contains("Direzione", case=False, na=False)]
    elif sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].str.contains("APE|Legge 10", case=False, na=False)]
    elif sezione == "PRATICHE":
        df_f = df[df['Pratica'].str.contains("CILA|SCIA|Accertamento|Paesaggistica", case=False, na=False)]
    else:
        df_f = df

    # Lista Clienti a sinistra, Scheda a destra
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        search = st.text_input("🔍 Cerca cliente...", label_visibility="collapsed")
        df_filt = df_f[df_f['Cliente'].str.contains(search, case=False)] if search else df_f
        
        for _, r in df_filt.iterrows():
            if st.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.lavoro_sel_id = int(r['id'])
                st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('lavoro_sel_id')
        if sel_id:
            # Recupero riga aggiornata dal DataFrame caricato
            r = df[df['id'] == sel_id].iloc[0]
            st.subheader(f"📑 {r['Cliente']} ({r['Pratica']})")
            
            # --- CHECKLIST INTEGRATA ---
            st.markdown("##### 🚦 Avanzamento Documenti")
            # Gestione sicura JSON (dict vs str)
            docs_raw = r['docs_json']
            if isinstance(docs_raw, str):
                docs_data = json.loads(docs_raw if docs_raw else "{}")
            else:
                docs_data = docs_raw if docs_raw else {}
                
            docs = inizializza_documenti(json.dumps(docs_data), r['Pratica'])
            nuovi_stati = {}

            for doc, stato in docs.items():
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"**{doc}**")
                
                opzioni = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
                def_idx = 0
                if "🟡" in stato: def_idx = 1
                elif "🟢" in stato: def_idx = 2
                
                res = c2.selectbox("Stato", opzioni, index=def_idx, key=f"check_{sel_id}_{doc}", label_visibility="collapsed")
                nuovi_stati[doc] = res
            
            st.markdown("---")
            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            # --- SALVATAGGIO SU SUPABASE ---
            if st.button("💾 SALVA AVANZAMENTO", use_container_width=True):
                sql = text('UPDATE lavori SET "docs_json" = :docs WHERE id = :id')
                conn.execute(sql, {"docs": json.dumps(nuovi_stati), "id": int(sel_id)})
                conn.commit()
                st.success("Stato Pratica Aggiornato su Cloud!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente per gestire la checklist")
