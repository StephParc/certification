import streamlit as st
import json
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="HBM Data Catalog", layout="wide")

# Fonction pour charger le JSON avec mise en cache (évite de recharger à chaque clic)
@st.cache_data
def load_data():
    # On cherche le fichier à la racine
    path = "data_catalog.json"
    if not os.path.exists(path):
        st.error(f"Fichier {path} introuvable à la racine !")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Injection de CSS pour changer la couleur des onglets en Bleu
st.markdown("""
<style>
    /* 1. Couleur de l'onglet sélectionné (le texte) */
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #007bff !important;
        font-weight: bold;
    }
    
    /* 2. La petite barre de soulignement sous l'onglet actif */
    div[data-baseweb="tab-highlight"] {
        background-color: #007bff !important;
    }

    /* 3. Couleur au survol pour les onglets non-sélectionnés */
    button[data-baseweb="tab"]:hover p {
        color: #0056b3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

catalog = load_data()

if catalog:
    st.title("🛡️ HBM Data Governance")
    st.markdown("---")

    # --- SECTION KPIs ---
    # Extraction des chiffres clés
    nb_sql = len(catalog.get('relational_db', []))
    nb_s3 = len([f for f in catalog.get('datalake', []) if not f.get('is_folder')])
    nb_nosql = len(catalog.get('nosql_db', []))

    col1, col2, col3 = st.columns(3)
    col1.metric("Tables SQL (Postgres)", f"{nb_sql} colonnes")
    col2.metric("Datalake", f"{nb_s3} objets")
    col3.metric("Collections NoSQL", f"{nb_nosql} sources")

    st.markdown("---")

    # --- SECTION EXPLORATION ---
    tab1, tab2, tab3 = st.tabs(["🛢️ Base Relationnelle", "☁️ Data Lake", "🍃 NoSQL MongoDB"])
    
    # A FAIRE PLUS TARD
    # + "🔗 Lignage des données"

    with tab1:
        st.subheader("Dictionnaire des données Postgres")
        if nb_sql > 0:
            df_sql = pd.DataFrame(catalog['relational_db'])
# 1. Groupe par Base
            for nom_base, group_base in df_sql.groupby('nom_base'):
                with st.expander(f"🛢️ **Base : {nom_base}**", expanded=False):
                    
                    # 2. Groupe par Schéma
                    for nom_schema, group_schema in group_base.groupby('schema'):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; Schéma : {nom_schema}")
                        
                        # 3. Groupe par Table
                        for nom_table, group_table in group_schema.groupby('nom_table'):
                            # On affiche le type de table à côté du nom (ex: BASE TABLE ou VIEW)
                            type_t = group_table['type_table'].iloc[0]
                            
                            with st.expander(f"&nbsp;&nbsp;&nbsp;&nbsp;{type_t} : {nom_table}"):
                                # 4. Affichage final des colonnes de la table
                                # On ne garde que les infos de colonnes pour le tableau final
                                cols_view = ['nom_colonne', 'type_data', 'nullable', 'contraintes', 'colonne_description']
                                st.dataframe(
                                    group_table[cols_view],
                                    width='stretch', 
                                    hide_index=True
                                )
        else:
            st.warning("Aucune donnée SQL trouvée.")

    with tab2:
        st.subheader("Inventaire des objets S3")
        if nb_s3 > 0:
            df_s3 = pd.DataFrame(catalog['datalake'])
            st.dataframe(df_s3[['bucket','path', 'file_name','size_ko', 'last_modified']], width='stretch')
        else:
            st.warning("Data Lake vide.")

    with tab3:
        st.subheader("Schémas MongoDB")
        for coll in catalog.get('nosql_db', []):
            with st.expander(f"📦 Collection : {coll['collection']}"):
                st.write(f"**Documents :** {coll['count']}")
                st.json(coll['fields'])

    # with tab_lineage:
    # st.subheader("Flux de données (Lineage)")
    # st.info("Visualisation du parcours de la donnée depuis l'ingestion jusqu'au stockage final.")
    
    # # Simulation visuelle du lignage par colonnes
    # c1, c2, c3 = st.columns(3)
    # with c1:
    #     st.markdown("### 📥 SOURCES")
    #     st.success("API External / IoT")
    #     st.success("Logs Serveurs")
    # with c2:
    #     st.markdown("### ⚙️ PROCESSING")
    #     st.button("Python Harvester ➔")
    # with c3:
    #     st.markdown("### 📂 DESTINATIONS")
    #     st.warning("Postgres (Relational)")
    #     st.warning("S3 (Object Storage)")
    #     st.warning("MongoDB (NoSQL)")