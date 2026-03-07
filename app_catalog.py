# app_catalogue.py
import streamlit as st
import json
import pandas as pd
import os
from utils.S3_utils import download_file
from config.config import PASSWORD_RW, PASSWORD_RO
import graphviz

# --- SYSTÈME DE LOGIN ---
def check_password():
    """Retourne True si l'utilisateur a saisi un mot de passe correct."""
    def password_entered():
        # Dictionnaire des utilisateurs (à mettre dans le .env en prod)
        users = {"admin": PASSWORD_RW, "user": PASSWORD_RO}
        if st.session_state["username"] in users and st.session_state["password"] == users[st.session_state["username"]]:
            st.session_state["password_correct"] = True
            st.session_state["role"] = "Admin" if st.session_state["username"] == "admin" else "User"
            del st.session_state["password"]  # On ne garde pas le mdp en mémoire
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Utilisateur", key="username")
        st.text_input("Mot de passe", type="password", key="password")
        st.button("Connexion", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.error("Utilisateur ou mot de passe incorrect")
        st.text_input("Utilisateur", key="username")
        st.text_input("Mot de passe", type="password", key="password")
        st.button("Connexion", on_click=password_entered)
        return False
    return True

if not check_password():
    st.stop() # Arrête l'exécution ici si pas connecté

# Bouton Déconnexion dans la barre latérale
if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.clear()
    st.rerun()

STORAGE_THRESHOLD_KO = 1048576 # 1Go
# Configuration de la page
st.set_page_config(page_title="HBM Data Catalog", layout="wide")

# Bouton de mise à jour manuelle dans la barre latérale
if st.sidebar.button("🔄 Forcer la mise à jour S3"):
    st.cache_data.clear()
    st.rerun()

# Fonction pour charger le JSON avec mise en cache (évite de recharger à chaque clic)
@st.cache_data
def load_data():
    # # On cherche le fichier à la racine
    # path = "data_catalog.json"
    # if not os.path.exists(path):
    #     st.error(f"Fichier {path} introuvable à la racine !")
    #     return None
    # with open(path, "r", encoding="utf-8") as f:
    #     return json.load(f)
    local_path = "data_catalog.json"
    # On récupère la version fraîche sur le Data Lake
    success = download_file(bucket="zone-config", s3_path="governance/data_catalog.json", local_path=local_path)
    
    if success and os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def format_taille(octets):
    if octets is None: return "0 o"
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if octets < 1024:
            return f"{octets:.1f} {unit}"
        octets /= 1024
    return f"{octets:.1f} To"

# Injection de CSS pour changer la couleur des onglets en Bleu
st.markdown("""
<style>
    /* 1. Couleur de l'onglet sélectionné (le texte) */
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #0072b2 !important;
        font-weight: bold;
    }
    
    /* 2. La petite barre de soulignement sous l'onglet actif */
    div[data-baseweb="tab-highlight"] {
        background-color: #0072b2 !important;
    }

    /* 3. Couleur au survol pour les onglets non-sélectionnés */
    button[data-baseweb="tab"]:hover p {
        color: #d55e00 !important;
    }

    h1 {
        margin-top: -10px !important;
        margin-bottom: -10px !important;
        padding-top: 20px !important;
        padding-bottom: 30px !important;
    }
    
    hr {
        margin-top: -40px !important;
        margin-bottom: -40px !important;
        padding-top: 0px !important;
        padding-bottom: 30px !important;
    }

    /* Réduire l'espace entre les rangées de colonnes */
    [data-testid="stVerticalBlock"] {
        gap: 1.2rem !important;
    }
    [data-testid="stMetric"] {
        border: 1px solid #d1d5db; 
        background-color: transparent; /* On laisse le thème de l'utilisateur gérer le fond */
        padding: 10px 15px !important;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: inherit !important; /* Respecte le thème Dark/Light */
    }

    </style>
    """, unsafe_allow_html=True)

catalog = load_data()

if catalog:
    search_query = st.text_input("🔍 Rechercher une donnée (table, colonne, fichier, collection...)", "").lower()
    st.markdown("---")
    df_sql = pd.DataFrame(catalog['relational_db'])
    if search_query and not df_sql.empty:
        df_sql = df_sql[
            df_sql['nom_table'].str.contains(search_query, case=False) | 
            df_sql['nom_colonne'].str.contains(search_query, case=False) |
            df_sql['colonne_description'].str.contains(search_query, case=False, na=False)
        ]

    items_s3 = catalog.get('datalake', {}).get('items', [])
    df_s3 = pd.DataFrame(items_s3)
    if search_query and not df_s3.empty:
        df_s3 = df_s3[
            df_s3['file_name'].str.contains(search_query, case=False, na=False) | 
            df_s3['path'].str.contains(search_query, case=False, na=False) |
            df_s3['bucket'].str.contains(search_query, case=False, na=False)
        ]

    nosql_data = catalog.get('nosql_db', [])
    if search_query:
        nosql_data = [
            coll for coll in nosql_data 
            if search_query in coll['collection'].lower() or 
            any(search_query in str(f).lower() for f in coll['fields'])
        ]

    st.title("🛡️ HBM Data Governance")
    st.markdown("---")

    # --- SECTION KPIs ---
    # Extraction des chiffres clés
    datalake_data = catalog.get('datalake', {})
    items_s3 = datalake_data.get('items', [])

    nb_sql = len(catalog.get('relational_db', []))
    items_s3_total = catalog.get('datalake',{}).get('items',[])
    nb_s3 = len([f for f in items_s3 if not f.get('is_folder')])
    nb_nosql = len(catalog.get('nosql_db', []))

    nb_sql_filtered = len(df_sql)
    nb_s3_filtered = len(df_s3)
    nb_nosql_filtered = len(nosql_data)

    st.markdown("##### 🌏 Vue générale")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tables SQL (Postgres)", f"{nb_sql} colonnes")
    with col2:
        st.metric("Datalake", f"{nb_s3} fichiers")
    with col3:
        st.metric("Collections NoSQL", f"{nb_nosql} collections")

    if search_query:
        st.markdown(f"##### 🎯 Pour ce critère : '*{search_query}*'")
        res1, res2, res3 = st.columns(3)
        with res1:
            st.metric("Postgres trouvés", nb_sql_filtered, delta=None)
        with res2:
            st.metric("S3 trouvés", nb_s3_filtered, delta=None)
        with res3:
            st.metric("NoSQL trouvés", nb_nosql_filtered, delta=None)
    else:
        st.info("💡 Tapez un mot-clé ci-dessus pour filtrer l'inventaire.")

    # col1.metric("Postgres", f"{len(df_sql)}/{len(catalog.get('relational_db', []))} col.")
    # col2.metric("Datalake", f"{len(df_s3)}/{len(items_s3)} fichiers")
    # col3.metric("NoSQL", f"{len(nosql_data)}/{len(catalog.get('nosql_db', []))} coll.")
    # col1.metric("Tables SQL (Postgres)", f"{nb_sql} colonnes")
    # col2.metric("Datalake", f"{nb_s3} objets")
    # col3.metric("Collections NoSQL", f"{nb_nosql} sources")

    st.markdown("---")

    # --- SECTION EXPLORATION ---
    tab_titles = ["🛢️ Base Relationnelle", "☁️ Data Lake", "🍃 NoSQL MongoDB", "🗺️ Lignage"]
    if st.session_state["role"] == "Admin":
        tab_titles += ["🏗️🩺 Santé"]

    tabs = st.tabs(tab_titles)

    # tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛢️ Base Relationnelle", "☁️ Data Lake", "🍃 NoSQL MongoDB", "🏗️🩺 Santé", "🗺️ Lignage"])

    with tabs[0]:
        st.subheader("Dictionnaire des données Postgres")
        if not df_sql.empty:
        # if nb_sql > 0:
            # df_sql = pd.DataFrame(catalog['relational_db'])
            # if search_query:
            #     df_sql = df_sql[
            #         df_sql['nom_table'].str.contains(search_query, case=False) | 
            #         df_sql['nom_colonne'].str.contains(search_query, case=False) |
            #         df_sql['colonne_description'].str.contains(search_query, case=False, na=False)
            #     ]

# 1. Groupe par Base
            for nom_base, group_base in df_sql.groupby('nom_base'):
                with st.expander(f"🛢️ **Base : {nom_base}**", expanded=False):
                    
                    # 2. Groupe par Schéma
                    for nom_schema, group_schema in group_base.groupby('schema'):
                        with st.expander(f"🌿 Schéma : {nom_schema}", expanded=False):
                        
                            # 3. Groupe par Table
                            for nom_table, group_table in group_schema.groupby('nom_table'):
                                # On affiche le type de table à côté du nom (ex: BASE TABLE ou VIEW)
                                type_t = group_table['type_table'].iloc[0]
                                nb_lignes = group_table['nb_lignes'].iloc[0]
                                taille = group_table['taille_octets'].iloc[0]
                                
                                if st.session_state["role"] != "Admin":
                                    # On retire les colonnes marquées "donnée sensible"
                                    group_table = group_table[~group_table['colonne_description'].str.contains("donnée sensible", na=False, case=False)]
                                    taille_display = "Masqué"
                                    lignes_display = "Masqué"
                                else:
                                    taille_display = format_taille(group_table['taille_octets'].iloc[0])
                                    lignes_display = f"{group_table['nb_lignes'].iloc[0]} lignes"

                                label_table = f"{type_t.upper()} : {nom_table} ({taille_display} | {lignes_display})"

                                # label_table = f"{type_t.upper()} : {nom_table} ({group_table['nb_lignes'].iloc[0]} lignes | {taille_display})"

                                # # On formate le label avec les stats
                                # label_table = f"{type_t.upper()} : {nom_table} ({nb_lignes} lignes | {format_taille(taille)})"
                                
                                with st.expander(f"&nbsp;&nbsp;&nbsp;&nbsp;{label_table}"):
                                    # 4. Affichage final des colonnes de la table
                                    # st.caption(f"📊 Volume total : {format_taille(taille)} | Enregistrements estimés : {nb_lignes}")
                                    # On ne garde que les infos de colonnes pour le tableau final
                                    cols_view = ['nom_colonne', 'type_data', 'nullable', 'contraintes', 'colonne_description']
                                    st.dataframe(
                                        group_table[cols_view],
                                        width='stretch', 
                                        hide_index=True
                                    )
        # else:
        #     st.warning("Aucune donnée SQL trouvée.")
        else:
            st.info("Aucun résultat dans Postgres")

    with tabs[1]:
        st.subheader("Inventaire des objets S3")
        if not df_s3.empty:
        # 1. On s'assure que les colonnes nécessaires existent
            cols_target = ['bucket', 'path', 'file_name', 'size_ko', 'last_modified']
            df_display = df_s3[df_s3.columns.intersection(cols_target)].copy()

            # 2. Groupe par Bucket
            for bucket_name, df_bucket in df_display.groupby('bucket'):
                with st.expander(f"🪣 **Bucket : {bucket_name}**", expanded=True):
                    
                    # On extrait le premier niveau du path pour faire des "dossiers"
                    # Ex: "E4/raw/events.csv" -> "E4"
                    df_bucket['folder'] = df_bucket['path'].apply(lambda x: x.split('/')[0] if pd.notnull(x) and '/' in x else "root")

                    # 3. Groupe par Dossier (Niveau 1)
                    for folder_name, df_folder in df_bucket.groupby('folder'):
                        icon_folder = "📁" if folder_name != "root" else "📄"
                        
                        with st.expander(f"    {icon_folder} Dossier : {folder_name}"):
                            # 4. Affichage des fichiers dans ce dossier
                            # On nettoie l'affichage pour ne pas répéter le bucket et le folder
                            final_cols = ['file_name', 'size_ko', 'last_modified']
                            st.dataframe(
                                df_folder[final_cols], 
                                use_container_width=True, 
                                hide_index=True
                            )   
        else:
            st.info("Aucun résultat dans le Data Lake")
        # if not df_s3.empty:
        # # if nb_s3 > 0:
        #     # df_s3 = pd.DataFrame(items_s3)
        #     # try:
        #     #     cols = [['bucket','path', 'file_name','size_ko', 'last_modified']]
        #     #     st.dataframe(df_s3[cols], width='stretch', hide_index=True)
        #     # except:
        #     #     st.info(f"Le datalake ne contient pas de fichier")
        #     cols_target = ['bucket','path', 'file_name','size_ko', 'last_modified']
        #     cols_final = df_s3.columns.intersection(cols_target)
        
        #     if not cols_final.empty:
        #         st.dataframe(df_s3[cols_final], width='stretch', hide_index=True)
        #     else:
        #         st.info("Les métadonnées S3 ne contiennent pas les colonnes standards")
        # # else:
        # #     st.warning("Data Lake vide.")
        # else:
        #     st.info("Aucun résultat dans le Data Lake")

    with tabs[2]:
        st.subheader("Schémas MongoDB")
        if nosql_data:
            for coll in nosql_data:
            # for coll in catalog.get('nosql_db', []):
                with st.expander(f"📦 Collection : {coll['collection']}"):
                    st.write(f"**Documents :** {coll['count']}")
                    st.json(coll['fields'])
        else:
            st.info("Aucun résultat dans MongoDB")

    with tabs[3]:    
        st.subheader("🔗 Lignage Visuel des données")
        tab_subtitles = ["⚙️ Transformation (dbt)", "📥 Ingestion (S3)"]
        if st.session_state["role"] == "Admin":
            tab_subtitles += ["🤖 Orchestration (DAGs)"]
        
        subtabs = st.tabs(tab_subtitles)

        with subtabs[0]:
            st.subheader("Dépendances des modèles SQL")
            nodes_dbt = catalog.get('dbt_nodes', {})
            edges_dbt = catalog.get('dbt_edges', [])
            
            if nodes_dbt:
                dot_dbt = graphviz.Digraph()
                dot_dbt.attr(rankdir='LR', size='10')
                colors = {"view": "#BBDEFB", "table": "#C8E6C9", "snapshot": "#F8BBD0"}
                
                for node_name, mat in nodes_dbt.items():
                    dot_dbt.node(node_name, f"{node_name}\n({mat})", fillcolor=colors.get(mat, "#EEEEEE"), style="filled", shape="box")
                for edge in edges_dbt:
                    dot_dbt.edge(edge['from'], edge['to'])
                st.graphviz_chart(dot_dbt)
            else:
                st.info("Aucun manifest dbt détecté.")

        with subtabs[1]:
                st.subheader("Inventaire S3 par familles")
                items_s3 = catalog.get('datalake', {}).get('items', [])
                
                if items_s3:
                    dot_files = graphviz.Digraph()
                    dot_files.attr(rankdir='LR', nodesep='0.1')
                    
                    # Logique de regroupement par préfixe (ex: musicshop_*, events_*)
                    grouped_prefixes = {}
                    for item in items_s3:
                        fname = item.get('file_name')
                        if not fname: continue
                        
                        # On détermine le préfixe (ce qui est avant le premier '_' ou '.')
                        prefix = fname.split('_')[0] if '_' in fname else fname.split('.')[0]
                        if prefix not in grouped_prefixes:
                            grouped_prefixes[prefix] = {"count": 0, "source": item.get('source'), "step": item.get('step')}
                        grouped_prefixes[prefix]["count"] += 1

                    for pref, info in grouped_prefixes.items():
                        label = f"📦 Family: {pref}_*\n({info['count']} fichiers)\nStep: {info['step']}"
                        dot_files.node(pref, label, shape="folder", fillcolor="#E1F5FE", style="filled")
                        # Optionnel : relier à la source
                        src = str(info['source'] or "Source").split(' ')[0]
                        dot_files.node(src, src, shape="ellipse")
                        dot_files.edge(src, pref)
                        
                    st.graphviz_chart(dot_files)

        # # On récupère les vraies données de lignage
        # items_s3 = catalog.get('datalake', {}).get('items', [])
        # steps_disponibles = sorted(list(set([str(i.get('step') or 'unknown') for i in items_s3])))
        # selected_steps = st.multiselect("🔍 Filtrer les étapes à afficher", 
        #                             options=steps_disponibles, 
        #                             default=steps_disponibles)
    
        if st.session_state["role"] == "Admin":
            with subtabs[2]:
                st.subheader("Flux par DAG Airflow")
                st.caption("Analyse statique des scripts Python dans le dossier /dags")
        
                airflow_logic = catalog.get('airflow_static_analysis', [])
                
                if airflow_logic:
                    dot_dag = graphviz.Digraph()
                    # 'rankdir' LR = Gauche à droite, 'splines' ortho = lignes droites
                    dot_dag.attr(rankdir='LR', splines='ortho', nodesep='0.4', ranksep='0.6') 
                    dot_dag.attr('node', fontname='Arial', fontsize='10', shape='rectangle', style='filled,rounded')

                    dot_dag.attr('node', 
                        shape='rectangle', 
                        style='filled,rounded', 
                        fillcolor='#F1F3F4',
                        fontname='Arial', 
                        fontsize='9',      # Police plus petite
                        height='0.3',      # Hauteur fixée
                        width='1.2',       # Largeur fixée
                        fixedsize='false') # S'adapte juste au texte mais reste petit

                    for dag in airflow_logic:
                        # On crée un cluster par fichier pour isoler les flux
                        with dot_dag.subgraph(name=f"cluster_{dag['dag_id']}") as c:
                            c.attr(label=f" 📄 Script: {dag['file']} ", style='rounded', color='#D1D5DB')
                            
                            # Le Noeud du DAG (en orange clair)
                            dag_node_id = f"dag_{dag['dag_id']}"
                            c.node(dag_node_id, f"📅 DAG: {dag['dag_id']}", fillcolor="#FFF3E0", color="#FFB74D")
                            
                            # Création des Tâches (en gris/bleu)
                            for t_id in dag['tasks']:
                                unique_id = f"{dag['dag_id']}_{t_id}"
                                c.node(unique_id, f"⚙️ {t_id}", fillcolor="#ECEFF1", color="#90A4AE")
                            
                            # Dessin des flèches séquentielles (>>)
                            if dag.get('dependencies'):
                                for edge in dag['dependencies']:
                                    c.edge(f"{dag['dag_id']}_{edge['from']}", f"{dag['dag_id']}_{edge['to']}", color="#546E7A")
                                
                                # On lie le DAG à la première tâche de la liste pour lancer le flux
                                first_task = dag['tasks'][0]
                                c.edge(dag_node_id, f"{dag['dag_id']}_{first_task}", style="dashed")
                            else:
                                # Fallback si pas de >> détectés
                                for t_id in dag['tasks']:
                                    c.edge(dag_node_id, f"{dag['dag_id']}_{t_id}", style="dotted")
                    
                    st.graphviz_chart(dot_dag, use_container_width=True)
                else:
                    st.info("Aucun script de DAG analysé.")          

    if st.session_state["role"] == "Admin":
        with tabs[4]:
            st.subheader("📦 Occupation du Data Lake")
            
            # Récupération du résumé calculé dans le harvester
            dl_summary = catalog.get('datalake', {}).get('summary', {})
            
            if dl_summary:
                alerts_found = False
                for bucket, stats in dl_summary.items():
                    size = stats.get('total_size_ko', 0)
                    if size > STORAGE_THRESHOLD_KO:
                        st.error(f"⚠️ **Alerte Quota** : Le bucket `{bucket}` dépasse le seuil critique ({round(size/1024, 2)} Mo / 1 Go)")
                        alerts_found = True
                
                if not alerts_found:
                    st.success("✅ Tous les volumes de stockage sont sous contrôle.")

                # Création d'un petit DataFrame pour un graphique
                df_storage = pd.DataFrame.from_dict(dl_summary, orient='index').reset_index()
                df_storage.columns = ['Bucket', 'Taille (Ko)', 'Nb Objets']
                
                # Affichage sous forme de colonnes de métriques
                cols = st.columns(len(dl_summary))
                for i, bucket in enumerate(dl_summary):
                    cols[i].metric(bucket, f"{dl_summary[bucket]['total_size_ko']} Ko")
                
                # Graphique en barres pour la visibilité
                st.bar_chart(df_storage.set_index('Bucket')['Taille (Ko)'])
            
            st.markdown("---")

            st.subheader("🖥️ État du Serveur")
            health = catalog.get('system_health', {})
            if health:
                c1, c2, c3 = st.columns(3)
                c1.metric("Disque Libre", f"{health['disk_free_gb']} GB")
                c2.metric("Usage RAM", f"{health['ram_usage_pct']}%")
                c3.info(f"Serveur: {health['server_name']} ({health['status']})")


        # # Filtrage des données
        # items_to_show = [i for i in items_s3 if str(i.get('step') or 'unknown') in selected_steps]
        # if items_to_show:
        #     dot = graphviz.Digraph(comment='Lignage Metadata')
        #    # Paramètres de compression
        #     dot.attr(rankdir='LR', size='12,12') # Taille maximale
        #     dot.attr(nodesep='0.1')   # Espace réduit entre les lignes (défaut: 0.25)
        #     dot.attr(ranksep='0.5')   # Espace réduit entre les colonnes (défaut: 0.5)
        #     dot.attr(concentrate='true') # Fusionne les flèches parallèles
        #     dot.attr(ratio='compress')   # Tente de faire tenir le tout dans l'espace imparti

        #     for item in items_to_show:
        #         # On récupère tes métadonnées spécifiques
        #         file_name = item.get('file_name')
        #         if not file_name:
        #             continue

        #         source_info = str(item.get('source') or 'Source inconnue')
        #         dag_info = str(item.get('dag') or 'Manuel')
        #         dest_info = str(item.get('destination') or 'N/A')
        #         step = str(item.get('step') or 'unknown')

        #         # Couleur selon le step
        #         color = "#E1F5FE" if "raw" in step.lower() else "#C8E6C9"
        #         dot.node(file_name, f"📄 {file_name}\n({step})", fillcolor=color)
                
        #         # 3. Création du Noeud Source
        #         # On prend le premier mot pour éviter les nœuds géants
        #         parts = source_info.split(' ')
        #         short_source = "Source"
                # for p in parts:
                #     if ".py" in p or "API" in p:
                #         short_source = p
                #         break
                # else:
                #     short_source = parts[0]
                # dot.node(short_source, short_source, shape='ellipse', fillcolor='#F5F5F5')
                # dot.edge(short_source, file_name, label=f"DAG: {dag_info}", fontsize='8', color='gray')

                # # 4. Création du Noeud Destination (si mentionné)
                # if dest_info and dest_info != 'N/A':
                #     # On simplifie le nom de destination
                #     short_dest = dest_info.split(' ')[0]
                #     dot.node(short_dest, short_dest, shape='cylinder', fillcolor='#FFF9C4')
                #     dot.edge(file_name, short_dest, label="Chargement", color='blue')

        #     st.graphviz_chart(dot, use_container_width=True)
        # else:
        #     st.info("Aucune donnée S3 disponible pour le lignage.")

        # 2. Création dynamique de la flèche "Source -> Fichier"


# *********************************
        # nodes_info = catalog.get('dbt_nodes', {})
        # edges_info = catalog.get('dbt_edges', [])
        
        # if nodes_info and edges_info:
        #     # Création du graphe
        #     dot = graphviz.Digraph(comment='Lignage Musicshop Dynamique')
        #     dot.attr(rankdir='LR') # De gauche à droite
        #     dot.attr('node', shape='box', style='filled', fontname='Arial')

        #     # Définition des couleurs par type de matérialisation
        #     # (Plus précis pour dbt que Bronze/Gold)
        #     colors = {
        #         "view": "#BBDEFB",      # Bleu (Views)
        #         "table": "#C8E6C9",     # Vert (Tables)
        #         "snapshot": "#F8BBD0",  # Rose (Snapshots)
        #         "source": "#B0BEC5"     # Gris (Sources raw)
        #     }

        #     # 1. On dessine les NOEUDS dynamiquement
        #     for node_name, materialized in nodes_info.items():
        #         fillcolor = colors.get(materialized, "#EEEEEE") # Couleur par défaut
        #         dot.node(node_name, f"{node_name}\n({materialized})", fillcolor=fillcolor)
            
        #     # 2. On dessine les LIENS dynamiquement
        #     for edge in edges_info:
        #         dot.edge(edge['from'], edge['to'])

        #     # 3. Affichage
        #     st.graphviz_chart(dot, use_container_width=True)
            
        #     st.info("💡 Ce graphe est généré automatiquement en analysant le `manifest.json` de dbt. Il reflète l'état réel de ton projet.")
            
        # else:
        #     st.warning("Données de lignage indisponibles. Assure-toi que le Harvester a pu lire le `manifest.json` de dbt (nécessite `dbt build`).")
