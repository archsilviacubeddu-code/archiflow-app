import streamlit as st
import pandas as pd
import json

# Lista Documenti Completa professionale
DOCUMENTI_BASE = [
    "CILA/SCIA/PdC", "Notifica Preliminare", "Contratto d'Appalto", 
    "Polizza RC Impresa", "DURC Valido", "P.O.S.", "P.S.C.", 
    "Visura Camerale", "Verbale Stato dei Luoghi", "Regolamento Condominio",
    "DiCo Impianti", "APE", "Variazione Catastale", "FIR (Rifiuti)"
]

def inizializza_documenti(riga_docs_json):
    try:
        if riga_docs_json and str(riga_docs_json) != "nan":
            return json.loads(riga_docs_json)
        return {}
    except:
        return {}

def interfaccia_semafori(id_cantiere, df_can, idx):
    st.write("### 🚦 Stato Documentazione")
    if 'docs_json' not in df_can.columns:
        df_can['docs_json'] = "{}"
    riga_json = df_can.at[idx, 'docs_json']
    docs_stato = inizializza_documenti(riga_json)
    elenco_totale = list(dict.fromkeys(DOCUMENTI_BASE + list(docs_stato.keys())))
    nuovi_stati = {}
    for i, doc in enumerate(elenco_totale):
        col_t, col_s = st.columns([3, 2])
        col_t.markdown(f"**{doc}**")
        attuale = docs_stato.get(doc, "🔴 Mancante")
        opzioni = ["🟢 Consegnato", "🟡 In Attesa", "🔴 Mancante"]
        scelta = col_s.selectbox(f"Stato {doc}", opzioni, index=opzioni.index(attuale) if attuale in opzioni else 2, key=f"sem_{id_cantiere}_{i}", label_visibility="collapsed")
        nuovi_stati[doc] = scelta
    st.divider()
    st.write("### ➕ Aggiungi Documento Extra")
    c_add1, c_add2 = st.columns([3, 1])
    nuovo_nome = c_add1.text_input("Nome documento...", key=f"in_add_{id_cantiere}")
    if st.button("💾 SALVA STATO DOCUMENTI", use_container_width=True, key=f"save_btn_{id_cantiere}"):
        if nuovo_nome: nuovi_stati[nuovo_nome] = "🔴 Mancante"
        df_can.at[idx, 'docs_json'] = json.dumps(nuovi_stati)
        return True
    return False

def widget_alert_home(df_can):
    st.markdown("---")
    st.subheader("⚠️ ALERT DOCUMENTI IN ATTESA")
    pendenti = []
    if 'docs_json' in df_can.columns:
        for _, r in df_can.iterrows():
            docs = inizializza_documenti(r['docs_json'])
            gialli = [n for n, s in docs.items() if "🟡" in s]
            if gialli:
                pendenti.append({"Cantiere": r['Cliente'], "Documenti in Attesa": ", ".join(gialli)})
    if pendenti:
        st.error("Documenti richiesti e non ancora consegnati:")
        st.table(pd.DataFrame(pendenti))
    else:
        st.success("Tutti i documenti sono in regola.")
