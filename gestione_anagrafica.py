import streamlit as st
import pandas as pd
from gestione_documenti import interfaccia_semafori

def mostra_anagrafica(df, DB_FILE, COLONNE):
    # CSS Custom (Il tuo stile originale, senza perdere un pixel)
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
        .btn-elimina-singolo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important; height: 45px !important; font-weight: bold !important;
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
            nuova_riga = pd.DataFrame([[nuovo_id, "", "", "", "", "", "", "", "", "Cantiere", "Da fare", "", "", "{}"]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()

    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            label_cliente = r['Cliente'] if r['Cliente'] != "" else "Nuovo Cliente (da nominare)"
            if st.button(f"👤 {label_cliente}", key=f"list_{r['id']}", use_container_width=True):
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
            u_pra = c6.selectbox("🏗️ Tipo Pratica", ["Cantiere", "Direzione lavori", "Progettazione", "APE", "Legge 10", "Altro"], index=0)
            u_sta = c7.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], index=0)
            u_sca = c8.text_input("📅 Scadenza", r['Scadenza'], placeholder="gg/mm/aaaa")
            
            c9, c10 = st.columns(2)
            u_tel = c9.text_input("📞 Telefono", r['Telefono'])
            u_mail = c10.text_input("📧 Email", r['Email'])
            
            u_note = st.text_area("📝 Note", r['Note'], height=120)

            # --- SEMAFORI DOCUMENTI (INTEGRATI) ---
            st.write("---")
            interfaccia_semafori(r['id'], df, idx)
            
            st.write("---")
            b_agg, b_del = st.columns(2)
            with b_agg:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("🔄 AGGIORNA E SALVA", use_container_width=True):
                    df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, u_ind_cantiere, u_pra, u_sta, u_sca, u_note, df.at[idx, 'docs_json']]
                    df.to_csv(DB_FILE, index=False)
                    st.success("Tutto salvato!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            with b_del:
                st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                if st.button("🗑️ ELIMINA", use_container_width=True):
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.session_state.cliente_sel = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
