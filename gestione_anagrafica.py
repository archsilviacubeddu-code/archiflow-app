import streamlit as st
import pandas as pd
import json
from sqlalchemy import text
from gestione_documenti import inizializza_documenti

def mostra_anagrafica(conn):
    # CSS per lo stile della pagina
    st.markdown("""
        <style>
        div[data-testid="stColumn"] {
            display: flex !important;
            align-items: flex-end !important;
        }
        div.stButton > button[key^="list_"] {
            height: 40px !important; width: 100% !important; text-align: left !important;
            border-radius: 8px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 14px !important;
            margin-bottom: -10px !important;
        }
        .header-btn > div > button {
            height: 45px !important; font-weight: 900 !important;
            border-radius: 10px !important;
        }
        .btn-new > div > button { background-color: #1e293b !important; color: white !important; }
        .btn-del > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        .btn-aggiorna > div > button { background-color: #457B9D !important; color: white !important; height: 45px !important; font-weight: bold !important; border: none !important; }
        .btn-checklist > div > button { background-color: #f59e0b !important; color: white !important; height: 45px !important; font-weight: bold !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # Lettura dati da Supabase
    df = pd.read_sql(text("SELECT * FROM lavori ORDER BY id DESC"), conn)

    # 1. BARRA SUPERIORE
    c_search, c_new, c_del = st.columns([2, 1, 1])
    
    with c_search:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra...", label_visibility="collapsed")
    
    with c_new:
        st.markdown('<div class="header-btn btn-new">', unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            sql = text('''INSERT INTO lavori 
                ("Cliente", "Pratica", "Stato", "docs_json", "Scadenza", "CF_PIVA", "Indirizzo", "CAP", "Citta", "Telefono", "Email", "Web", "Note") 
                VALUES (:cli, :pra, :sta, :docs, :sca, :cf, :ind, :cap, :cit, :tel, :mail, :web, :note) 
                RETURNING id''')
            
            params = {
                "cli": "", "pra": "Altro", "sta": "Da fare", "docs": "{}", 
                "sca": "", "cf": "", "ind": "", "cap": "", "cit": "", 
                "tel": "", "mail": "", "web": "", "note": ""
            }
            
            result = conn.execute(sql, params)
            new_id = result.fetchone()[0]
            conn.commit()
            st.session_state.cliente_sel_id = int(new_id)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_del:
        st.markdown('<div class="header-btn btn-del">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [int(k.replace("check_", "")) for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                sql = text("DELETE FROM lavori WHERE id IN :ids")
                conn.execute(sql, {"ids": tuple(selezionati)})
                conn.commit()
                st.session_state.cliente_sel_id = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. LISTA E SCHEDA
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
        for _, r in df_filt.iterrows():
            cl1, cl2 = st.columns([0.15, 0.85])
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            label_cliente = r['Cliente'] if r['Cliente'] else "📝 (Nuova voce vuota)"
            if cl2.button(f"👤 {label_cliente}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel_id = int(r['id'])
                st.rerun()

    with col_scheda:
        sel_id = st.session_state.get('cliente_sel_id')
        if sel_id:
            res = pd.read_sql(text("SELECT * FROM lavori WHERE id = :id"), conn, params={"id": sel_id})
            if not res.empty:
                r = res.iloc[0]
                st.subheader(f"📑 {r['Cliente'] if r['Cliente'] else 'Nuova Pratica'}")
                
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
                lista_pratiche = ["Cantiere interni", "Cantiere esterni", "Direzione lavori", "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", "Accertamento di conformità", "Millesimi", "Perizia", "Accesso atti", "Render", "Altro"]
                u_pra = c6.selectbox("Pratica", lista_pratiche, index=lista_pratiche.index(r['Pratica']) if r['Pratica'] in lista_pratiche else 13)
                
                stati_possibili = ["Da fare", "In corso", "Annullata", "Conclusa", "Sospesa"]
                u_sta = c7.selectbox("Stato", stati_possibili, index=stati_possibili.index(r['Stato']) if r['Stato'] in stati_possibili else 0)
                u_sca = c8.text_input("📅 Scadenza", r['Scadenza'])

                c9, c10 = st.columns(2)
                u_tel = c9.text_input("Telefono", r['Telefono'])
                u_mail = c10.text_input("Email", r['Email'])
                u_note = st.text_area("Note", r['Note'], height=100)

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                    if st.button("🔄 AGGIORNA DATI", use_container_width=True):
                        sql = text('''UPDATE lavori SET 
                                    "Cliente"=:cli, "CF_PIVA"=:cf, "Indirizzo"=:ind, "CAP"=:cap, "Citta"=:cit, 
                                    "Telefono"=:tel, "Email"=:mail, "Web"=:web, "Pratica"=:pra, "Stato"=:sta, 
                                    "Scadenza"=:sca, "Note"=:note WHERE id=:id''')
                        conn.execute(sql, {
                            "cli": u_cli, "cf": u_cf, "ind": u_ind, "cap": u_cap, "cit": u_cit,
                            "tel": u_tel, "mail": u_mail, "web": u_web, "pra": u_pra, 
                            "sta": u_sta, "sca": u_sca, "note": u_note, "id": sel_id
                        })
                        conn.commit()
                        st.success("Salvato!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with b_col2:
                    st.markdown('<div class="btn-checklist">', unsafe_allow_html=True)
                    if st.button("📋 CHECKLIST", use_container_width=True):
                        # Nota: r['docs_json'] in PostgreSQL potrebbe essere già un dict
                        docs_data = r['docs_json'] if isinstance(r['docs_json'], dict) else json.loads(r['docs_json'] or "{}")
                        apri_checklist(conn, sel_id, u_pra, docs_data)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Seleziona un cliente.")

@st.dialog("Gestione Checklist")
def apri_checklist(conn, sel_id, pratica, docs_json):
    st.write(f"Documenti per: **{pratica}**")
    # Passiamo il dizionario direttamente
    docs = inizializza_documenti(json.dumps(docs_json), pratica)
    nuovi_stati = {}
    for d, s in docs.items():
        cx1, cx2 = st.columns([3, 2])
        cx1.markdown(f"**{d}**")
        opz = ["🔴 Da fare", "🟡 In Attesa", "🟢 Fatto"]
        # Normalizziamo lo stato per trovare l'indice
        idx = 0
        if "🟡" in s or "Attesa" in s: idx = 1
        elif "🟢" in s or "Fatto" in s: idx = 2
        
        nuovi_stati[d] = cx2.selectbox(f"S_{d}", opz, index=idx, key=f"pop_{d}", label_visibility="collapsed")
    
    st.divider()
    if st.button("💾 SALVA E CHIUDI", use_container_width=True):
        sql = text('UPDATE lavori SET "docs_json" = :docs WHERE id = :id')
        conn.execute(sql, {"docs": json.dumps(nuovi_stati), "id": sel_id})
        conn.commit()
        st.rerun()
