#!/usr/bin/python
# -*- coding: latin-1 -*-

import subprocess
import sys
import sqlite3

def installBdd():
	#Installation SQLITE et PIP
	print 'Installation prérequis [En cours]'
	subprocess.call('apt-get install python-pip sqlite3 openssh-server git -y > /dev/null 2>&1',shell=True)
	#Installation lib paramiko
	subprocess.call('pip install paramiko > /dev/null 2>&1',shell=True)
	print 'Installation prérequis      [OK]'

	#Creation dossier gestion CSF
	subprocess.call('mkdir /srv/csf',shell=True)
	subprocess.call('mkdir /srv/csf/script',shell=True)
	print 'Création dossier gestion    [OK]'

	#Copie fichiers vers dossier CSF
	subprocess.call('cp ./mod_csf.conf /srv/csf',shell=True)
	subprocess.call('cp ./tmpip.conf /srv/csf',shell=True)
	subprocess.call('cp ./script/* /srv/csf/Script',shell=True)

	subprocess.call('sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config',shell=True)
	subprocess.call('systemctl restart sshd',shell=True)
	print 'Configuration SSH           [OK]'

	subprocess.call('ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N "" > /dev/null 2>&1',shell=True)
	print 'Génération clé SSH          [OK]'

	print 'Configuration environnement [OK]'
	print 'Installation prérequis BDD  [OK]'
	
def configBdd():
	#Creation BDD pour CSF
	conn = sqlite3.connect('/srv/csf/bdd.db')
	#Curseur pour modification BDD
	cursor = conn.cursor()
	#Creation Table BDD
	cursor.execute('''CREATE TABLE neighbors
    (id INTEGER NOT NULL, ip TEXT NOT NULL PRIMARY KEY, desc TEXT NOT NULL)''')
	cursor.execute('''CREATE TABLE key
    (id INTEGER PRIMARY KEY NOT NULL, key TEXT NOT NULL, desc TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE snort
    (id INTEGER PRIMARY KEY NOT NULL, amert TEXT NOT NULL)''')
	#Ajout de la clé pour la communication neighbors
	keyCsf = 'fyoQ3Zm8nVvE0BGV'
	cursor.execute('INSERT INTO key VALUES (1,"' + keyCsf + '","Key Cluster");')
	#Commit BDD
	conn.commit()
	#Fermeture curseur et bdd
	cursor.close()
	conn.close()

	print 'Configuration BDD           [OK]'

def cronMaj():
	fTmp = '/tmp/task.txt'
	cmdEcho = 'echo "*/1 * * * * python /srv/csf/script/maj.py" >> ' + fTmp 
	cmdCron = 'crontab ' + fTmp 
	cmdRm = 'rm ' + fTmp
	subprocess.call(cmdEcho,shell=True)
	subprocess.call(cmdCron,shell=True)
	subprocess.call(cmdRm,shell=True)

	print 'Configuration Crontab       [OK]'
	

####################
# Installation BDD #
####################
installBdd()

#####################
# Configuration BDD #
#####################
configBdd()

#########################
# Configuration Crontab #
#########################
cronMaj()
