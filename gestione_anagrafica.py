import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COL_ANAGRAFICA):
    st.header("📇 Gestione Anagrafica")
    
    # Intestazione Tabella con la tua formattazione
    h = st.columns([1.5, 1.5, 1.5, 1, 1, 1, 1, 4.5])
    labels = ["Cliente", "C.F./P.IVA", "Indirizzo", "Telefono", "Email", "Pratica", "Stato", "Azioni"]
    for i, label in enumerate(labels): 
        h[i].markdown(f'<div class="table-header">{label}</div>', unsafe_allow_html=True)

    for i, r in df.iterrows():
        c = st.columns([1.5, 1.5, 1.5, 1, 1, 1, 1, 4.5])
        u_cli = c[0].text_input("Cli", r['Cliente'], key=f"cli_{i}", label_visibility="collapsed")
        u_cf = c[1].text_input("CF", r['C.F. / P.IVA'], key=f"cf_{i}", label_visibility="collapsed")
        u_ind = c[2].text_input("Ind", r['Indirizzo'], key=f"ind_{i}", label_visibility="collapsed")
        u_tel = c[3].text_input("Tel", r['Telefono'], key=f"tel_{i}", label_visibility="collapsed")
        u_mail = c[4].text_input("Mail", r['Email'], key=f"mail_{i}", label_visibility="collapsed")
        u_pra = c[5].text_input("Pra", r['Pratica'], key=f"pra_{i}", label_visibility="collapsed")
        u_sta = c[6].selectbox("Sta", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1, key=f"sta_{i}", label_visibility="collapsed")
        
        btns = c[7].columns(3)
        if btns[0].button("🔄\nAGGIORNA", key=f"up_{i}"):
            df.loc[i] = [r['id'], u_cli, u_cf, u_ind, r['CAP'], r['Città'], u_tel, u_mail, r['Web'], u_pra, u_sta, r['Scadenza'], r['Note']]
            df.to_csv(DB_FILE, index=False)
            st.rerun()
        if btns[1].button("📂\nAPRI", key=f"op_{i}"):
            st.info(f"Apertura scheda {u_cli}...")
        if btns[2].button("🗑️\nCANCELLA", key=f"del_{i}"):
            df.drop(i).to_csv(DB_FILE, index=False)
            st.rerun()
