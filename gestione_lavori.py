import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    # CSS per i bottoni giganti e colorati
    st.markdown("""
        <style>
        .btn-lavoro > div > button {
            height: 10em !important;
            font-size: 20px !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            color: white !important;
            margin-bottom: 20px !important;
            white-space: pre-line !important;
        }
        /* Colori */
        .btn-dl > div > button { background-color: #E63946 !important; }    /* Rosso */
        .btn-pra > div > button { background-color: #457B9D !important; }   /* Blu */
        .btn-ape > div > button { background-color: #2A9D8F !important; }   /* Verde */
        .btn-alt > div > button { background-color: #6C757D !important; }   /* Grigio */
        </style>
    """, unsafe_allow_html=True)

    # Navigazione interna
    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None

    if st.session_state.sezione_lavoro:
        sezione = st.session_state.sezione_lavoro
        
        if st.button("⬅️ TORNA AI LAVORI"):
            st.session_state.sezione_lavoro = None
            st.rerun()
            
        st.header(f"📂 {sezione.upper()}")
        st.divider()

        # Filtro basato sulle scelte dell'anagrafica
        if sezione == "APE / LEGGE 10":
            df_filtro = df[df['Pratica'].isin(["APE", "Legge 10"])]
        elif sezione == "ALTRO":
            # Filtra tutto ciò che non è nelle tre categorie principali
            opzioni_standard = ["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"]
            df_filtro = df[~df['Pratica'].isin(opzioni_standard)]
        else:
            # Corrispondenza esatta per Direzione lavori e Pratica urbanistica
            df_filtro = df[df['Pratica'] == sezione]

        if df_filtro.empty:
            st.info(f"Nessuna pratica trovata per: {sezione}")
        else:
            for i, r in df_filtro.iterrows():
                with st.expander(f"👤 {r['Cliente']} - 📍 {r['Web']}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Stato:** {r['Stato']}")
                    c1.write(f"**Scadenza:** {r['Scadenza']}")
                    c2.write(f"**Tel:** {r['Telefono']}")
                    c2.write(f"**Email:** {r['Email']}")
                    st.write(f"**Note:** {r['Note']}")
                    
                    # Spazio per bottoni futuri (Verbali, DOC, ecc.)
                    if sezione == "Direzione lavori":
                        st.button(f"🎙️ Diario Cantiere", key=f"btn_dl_{r['id']}")
    else:
        # DASHBOARD A 4 BOTTONI
        st.title("🏗️ Area Lavori")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
