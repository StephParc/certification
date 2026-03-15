
# Projet pour le titre RCNP 37638 "Expert en infrastructures de données massives"

Ce projet entre dans le cadre d'une certification pour l'obtention du titre RNCP 37638.
A cette fin, 7 rendus sont attendus dénommés E1 à E7. Les trois premiers font appel à de la gestion de projet, E4 concerne les bases de données, E5 et E6 les datawarehouse, E7 le datalake. Chacun est détaillé dans la page associée.  
Vous trouverez le détail du référentiel à l'adresse suivante [https://www.francecompetences.fr/recherche/rncp/37638/](https://www.francecompetences.fr/recherche/rncp/37638/)

Le projet est construit sur le langage python, ses frameworks et bibliothèques.


## Prérequis

L'architecture est entièrement dockérisée. Les seules installations nécessaires sont git (pour cloner le projet) et Docker.
Vous trouverez de quoi les faire aux adresses suivantes:   
[https://git-scm.com/book/fr/v2/D%C3%A9marrage-rapide-Installation-de-Git](https://git-scm.com/book/fr/v2/D%C3%A9marrage-rapide-Installation-de-Git)  
[https://docs.docker.com/](https://docs.docker.com/)  

Pour le reproduire dans son intégralité sans modification, il est également nécessaire de sourcrire à un compte Ngrok (version gratuite suffisante, pas d'installation nécessaire). Vous pouvez le faire [https://ngrok.com/](https://ngrok.com/).  
Sans cela, il faut décommenter les ports du docker-compose.yml pour revenir à l'exposition localhost standard.  


La partie E5 est alimentée par l'API Ticketmaster qui nécessite également une inscription (gratuite) pour obtenir les clés.   [https://developer.ticketmaster.com/](https://developer.ticketmaster.com/)  
Elle n'est toutefois pas indispensable. Seul le DAG daily_ticketmaster_update_dag.py y fait appel, il suffit de ne pas l'activer voire de le supprimer.  

J'ai prévu un alerting sur un serveur de messagerie qui peut-être commenté ou supprimé dans les DAG Airflow concernés. J'ai utilisé Discord mais n'importe quel service équivalent proposant des Webhook convient.  


## Confort d'utilisation

Bien que non nécessaires au projet, il est appréciable de pouvoir interagir avec des utilitaires graphiques. Je vous en conseille pour Docker (Docker Desktop), PostgreSQL (DBeaver, DbVisualizer, ou autre), MongoDB (MongoDB Compass) et Garage (fortement recommandé; par exemple WinSCP [https://winscp.net/eng/download.php](https://winscp.net/eng/download.php) pour Windows sinon FileZilla ou Nautilus de Gnome)  
J'ai précisé mes propres paramétrages dans un onglet dédié.  


## Installation

L'installation est extrêmement simplifiée grâce à un script de configuration et déploiement.  

Procédure:  
- faire un git clone du projet
- renseigner le fichier .env.template (il sera renommé pendant l'installation, pas besoin de le faire).
- dans setup_infra.sh, si vous n'êtes pas dans un environnement avec poetry, commenter les lignes 10 à 17 (marquées "bloc optionnel")  
- s'assurer que le setup_infra.sh soit exécutable sinon exécuter en ligne de commande `chmod +x setup_infra.sh` depuis le répertoire où il se trouve
- exécuter le script `./setup_infra.sh` , renseigner votre mot de passe si besoin
- si Airflow rencontre des problèmes de permissions, vérifier le groupe avec une des commandes `getent group docker | cut -d: -f3` ou `stat -c '%g' /var/run/docker.sock` puis remplacer la valeur de group_add des services airflow_webserver et airflow_scheduler par la valeur obtenue dans le docker-compose.yml. Refaire un `docker compose up -d`  
- supprimer les services nginx et ngrok si vous ne les utilisez pas et décommenter les ports des autres services  

L'architecture est prête, il reste à peupler les bases. Un jeu de départ est prévu à l'aide de fichiers.   
Pour cela rendez-vous sur votre domaine Ngrok, https://DOMAIN_A_REMPLACER.ngrok-free.dev/airflow ou http://localhost:8080/ si avez choisi de rester en local.  

Exécuter les DAGs dans cet ordre:  
Pour E4:   
- setup_hbm_sql.py (les tables se créent avec jeu de démo)
- sync_mongo_sql.py (synchronise les deux bases)
- daily_events_update.py (pour les traitements réguliers)
- daily_scrapy_update.py (pour les traitements réguliers)  

Pour E5:  
- ticketmaster_etl_pipeline.py (traitement régulier Ticketmaster)  

Pour E6:  
- setup_musicshop_initialisation.py (génère des clients aléatoires)
- daily_exchange_rates.py (génère des taux de change quotidiens)
- daily_orders_pipeline.py (génère des commandes. Nécessite que la table TB_partition existe et soit alimentée DAG *setup_hbm_sql.py*)  
- musicshop_gold_transformation.py

## Configurations supplémentaires

Selon le système d'installation, il peut être nécessaire de faire des ajustements dans postgresql.conf, pg_hba.conf et .gitattributes (encodage avec "locale", communications intérieures/extérieures docker avec "listen_addresses", chemins et fins de lignes CRLF vs LF des scripts)
 





