# Installation Base de données

Ce repository permet de déployer une base de données SQLite version 3 pour l'intégration des données pour la mise en place d'un cluster CSF avec mise à jour des règles pour SNORT


# Description automatisation
Lors du lancement du script, un dossier csf est crée dans **/srv** du serveur. 

Ce dossier contient tous les fichiers nécessaires au bon fonctionnement de l'automatisation dont le rôle de chaque fichier est le suivant :

 - **install.py** : script installation BDD
 - **mod_csf.conf** : fichier modèle pour la configuration CSF. Ce fichier sert à la génération du fichier final
 - **mod_csf.blacklists** : fichier modèle pour la définition de la blacklists CSF. Ce fichier est envoyé à chaque CSF
 - **tmpip.conf** : fichier temporaire pour la récupération des IP de chaque serveur. Il permet l'intégration des données dans la base de données
 - **maj_csf.py** : script de mise à jour manuelle de la configuration CSF en cas de modification du fichier **mod_csf.conf** par l'utilisateur.  

## Lancement script installation

Pour lancer l'automatisation de l'installation, il faut lancer la commande **python install.py**

>**Prérequis :**
>  - être sous le compte **root** de la machine
>  - connection à internet fonctionnelle

## Mise à jour Base de données
Lors de l'installation, une tâche **CRON** est mise en place qui permet d'interroger l'état du serveur.

Les différents états :

 - **Vide** = Aucune mise à jour à effectuer
 - **BDD** = Un nouveau serveur est installé. Les informations (IP, Nom) vont être intégrées dans la base
 - **CSF** = La base de données est parsée pour déclarer les serveurs CSF afin de monter le cluster. Un fichier de configuration est généré et envoyé en SSH vers les IP présentes dans la base. 

> Le fichier d'état de la mise à jour est disponible dans **/srv/csf/script/state.conf**
