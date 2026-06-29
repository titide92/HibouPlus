import streamlit as st
import pandas as pd

from hibou_automation import HibouAutomation

st.set_page_config(page_title="HibouPlus", page_icon="📚", layout="wide")

st.title("HibouPlus")
st.caption("Interface de gestion Hibouthèque")

if "automation" not in st.session_state:
    st.session_state.automation = None
if "status_log" not in st.session_state:
    st.session_state.status_log = []
if "imported_rows" not in st.session_state:
    st.session_state.imported_rows = []
if "login" not in st.session_state:
    st.session_state.login = ""
if "password" not in st.session_state:
    st.session_state.password = ""


def append_log(message: str) -> None:
    st.session_state.status_log.append(message)
    if len(st.session_state.status_log) > 50:
        st.session_state.status_log = st.session_state.status_log[-50:]


st.sidebar.header("Connexion")
st.session_state.login = st.sidebar.text_input("Identifiant", value=st.session_state.login)
st.session_state.password = st.sidebar.text_input("Mot de passe", value=st.session_state.password, type="password")

col_init, col_close = st.sidebar.columns(2)
with col_init:
    if st.sidebar.button("Initialiser"):
        try:
            automation = HibouAutomation()
            automation.login = st.session_state.login
            automation.password = st.session_state.password
            automation.prepare_for_operations()
            st.session_state.automation = automation
            append_log("✓ Session prête")
            st.success("Session prête")
        except Exception as exc:
            append_log(f"❌ {exc}")
            st.error(str(exc))

with col_close:
    if st.sidebar.button("Déconnexion"):
        if st.session_state.automation is not None:
            try:
                st.session_state.automation.cleanup()
            except Exception:
                pass
        st.session_state.automation = None
        append_log("↪ Déconnexion effectuée")
        st.info("Déconnexion effectuée")

if st.session_state.automation is not None:
    st.sidebar.success("Connexion active")
else:
    st.sidebar.info("La session n'est pas encore initialisée")

st.header("Étapes de connexion et d'exécution")
status_col1, status_col2 = st.columns(2)
with status_col1:
    st.subheader("Étapes")
    steps = [
        "1. Saisir vos identifiants",
        "2. Initialiser la session",
        "3. Vérifier la connexion au site",
        "4. Se positionner sur la page prêt/retour",
        "5. Utiliser les actions ci-dessous",
    ]
    for step in steps:
        st.write(step)

with status_col2:
    st.subheader("Journal d'actions")
    if st.session_state.status_log:
        for item in reversed(st.session_state.status_log):
            st.write(item)
    else:
        st.write("Aucune action pour le moment")

st.header("Actions")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Rendre un livre")
    return_entry = st.text_input("Saisissez l'identifiant de l'exemplaire", key="return_entry")
    if st.button("Rendre un livre", disabled=st.session_state.automation is None):
        if st.session_state.automation is None:
            st.error("Initialisez d'abord la session")
        elif return_entry:
            try:
                st.session_state.automation.process_manual_entry(return_entry, action_label="Retour")
                append_log(f"Retour traité : {return_entry}")
                st.success("Retour traité")
            except Exception as exc:
                append_log(f"❌ {exc}")
                st.error(str(exc))
        else:
            st.warning("Saisissez une valeur avant de valider")

with col2:
    st.subheader("Emprunter un livre")
    borrow_entry = st.text_input("Saisissez l'identifiant de l'exemplaire ou %numéro d'emprunteur", key="borrow_entry")
    if st.button("Emprunter un livre", disabled=st.session_state.automation is None):
        if st.session_state.automation is None:
            st.error("Initialisez d'abord la session")
        elif borrow_entry:
            try:
                st.session_state.automation.process_manual_entry(borrow_entry, action_label="Emprunt")
                append_log(f"Emprunt traité : {borrow_entry}")
                st.success("Emprunt traité")
            except Exception as exc:
                append_log(f"❌ {exc}")
                st.error(str(exc))
        else:
            st.warning("Saisissez une valeur avant de valider")

with col3:
    st.subheader("Importer une base de livres")
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.imported_rows = df.to_dict(orient="records")
            append_log(f"✓ {len(st.session_state.imported_rows)} lignes importées")
            st.success(f"{len(st.session_state.imported_rows)} lignes importées")
            st.dataframe(df.head())
        except Exception as exc:
            append_log(f"❌ {exc}")
            st.error(str(exc))

    if st.button("Traiter la base importée", disabled=st.session_state.automation is None):
        if st.session_state.automation is None:
            st.error("Initialisez d'abord la session")
        elif not st.session_state.imported_rows:
            st.warning("Aucune base importée")
        else:
            try:
                for row in st.session_state.imported_rows:
                    entry = row.get("entry") or row.get("code") or row.get("exemplaire") or row.get("livre")
                    if entry:
                        st.session_state.automation.process_manual_entry(str(entry), action_label="Import")
                append_log("✓ Base traitée")
                st.success("Base traitée")
            except Exception as exc:
                append_log(f"❌ {exc}")
                st.error(str(exc))
