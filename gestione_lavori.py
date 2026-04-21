import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    st.markdown("""
        <style>
        /* DASHBOARD PRINCIPALE */
        .btn-lavoro > div > button {
            height: 10em !important; font-size: 20px !important; border-radius: 20px !important;
            font-weight: bold !important; color: white !important; margin-bottom: 20px !important; white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }

        /* LISTA SINISTRA (Stile Anagrafica) */
        div.stButton > button[key^="list_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 15px !important;
        }
        
        /* TASTO BACK PICCOLO */
        div.stButton > button[key="btn_back"] {
            height: 32px !important; width: 80px !important; font-size: 12px !important;
            margin-bottom: 15px !important; padding: 0px !important;
        }

        /* BOTTONI AZIONE SUPERIORI */
        div.stButton > button[key="btn_new"], .btn-del-massivo > div > button {
            height: 45px !important; font-weight: bold !important; margin-top: 5px !important;
        }
        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important;
        }

        /* BOTTONI SCHEDA */
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important; height: 45px !important; font-weight: bold !important;
        }
        .btn-elimina-singolo > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; height: 45px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None
    if "lavoro_sel" not in st.session_state:
        st.session_state.lavoro_sel = None

    if st.session_state.sezione_lavoro:
        render_modulo_lavoro(st.session_state.sezione_lavoro, df, DB_FILE)
    else:
        # DASHBOARD PRINCIPALE
        st.header("🏗️ Selezione Area di Lavoro")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_modulo_lavoro(sezione, df, DB_FILE):
    # Filtro dati per categoria
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 1
