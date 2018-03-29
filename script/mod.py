#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import subprocess
import sqlite3
import paramiko
import socket
import getpass
import tarfile

#######
# SSH #
#######

def connSsh(a):
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(a, username='root')

	return client

#######
# CSF #
####### 

def majCsf(a):
	neighbors = neighborsCsf()
	keyCluster = keyCsf()
	confCsf(neighbors,keyCluster)
	sendPara(neighbors)

	if a == 1:
		subprocess.call('echo "" > /srv/csf/script/state.conf',shell=True)

def neighborsCsf():
	conn = sqlite3.connect('/srv/csf/bdd.db')
	c = conn.cursor()
	c.execute('SELECT * FROM neighbors;')
	nbIp = c.fetchall()
	listIp = []

	for i in nbIp:
		listIp.append(i[1])

	conn.close()
	return listIp

def keyCsf():
	conn = sqlite3.connect('/srv/csf/bdd.db')
	c = conn.cursor()
	c.execute('SELECT * FROM key WHERE desc = "Key Cluster";')
	key = c.fetchone()

	conn.close()
	return key[1]

def confCsf(a,b):
	oldConf = open('/srv/csf/mod_csf.conf','r')
	
	texte = oldConf.readlines()

	send = 'CLUSTER_SENDTO = ""'
	master = 'CLUSTER_MASTER = ""'
	receive = 'CLUSTER_RECVFROM = ""'
	config = 'CLUSTER_CONFIG = "0"'
	key = 'CLUSTER_KEY = ""'

	for ListCsf in a:
		newConf = open('/srv/csf/csf' + ListCsf + '.conf','w')
		listIp = []

		for ListCsf2 in a:
			if ListCsf != ListCsf2:			
				listIp.append(ListCsf2)

		ip = ','.join(listIp)

		for ligne in texte:
			if send in ligne:
				newConf.write('CLUSTER_SENDTO = "' + ip + '"' + '\n')
			elif master in ligne:
				newConf.write('CLUSTER_MASTER = "' + a[0] + '"' + '\n')
			elif receive in ligne:
				newConf.write('CLUSTER_RECVFROM = "' + ip + '"' + '\n')
			elif config in ligne:
				newConf.write('CLUSTER_CONFIG = "1"' + '\n')
			elif key in ligne:
				newConf.write('CLUSTER_KEY = "' + str(b) + '"' + '\n')
			else:
				newConf.write(ligne)

		newConf.close()
	oldConf.close()
	
def sendPara(a):

		for ip in a:

			sftp = connSsh(ip).open_sftp()
			source = '/srv/csf/csf'+ ip + '.conf'
			destination = '/etc/csf/csf.conf'
			sftp.put(source,destination)

			fBlock = '/srv/csf/mod_csf.blocklists'
			fOldBlock = '/etc/csf/csf.blocklists'
			sftp.put(fBlock,fOldBlock)

			sftp.close()

		subprocess.call('rm /srv/csf/csf*',shell=True)

#######
# BDD #
#######

def majBdd():

	conn = sqlite3.connect('/srv/csf/bdd.db')
	cursor = conn.cursor()
	cursor.execute('SELECT id FROM neighbors WHERE id = (SELECT MAX(id) FROM neighbors);')
	lastId = cursor.fetchone()

	if str(lastId) == 'None':
		nextId = 1
	else:
		nextId = lastId[0] + 1

	tmpIp = open('/srv/csf/tmpip.conf','r')
	lines = tmpIp.readlines()

	for line in lines:

		if len(line) > 1:

			ip = line.split(',')
			ip = ip[0]
			hostname = line.split(',')
			hostname = hostname[1]

			reqSql = 'INSERT INTO neighbors VALUES (' + str(nextId) + ',"' + ip + '","' + hostname + '");'

			cursor.execute(reqSql)

			nextId += 1

	conn.commit()
	cursor.close()
	conn.close()

	subprocess.call('echo "" > /srv/csf/tmpip.conf',shell=True)
	subprocess.call('echo "CSF" > /srv/csf/script/state.conf',shell=True)

#########
# SNORT #
#########

def majSnort(a):

	subprocess.call('wget https://www.snort.org/downloads/community/community-rules.tar.gz > /dev/null 2>&1',shell=True)
	tar = tarfile.open('./community-rules.tar.gz')
	tar.extractall(path='/srv/csf/')
	tar.close()
	subprocess.call('rm ./community-rules.tar.gz')

	oldConf = open('/srv/csf/community-rules/community.rules','r')
	newConf = open('/srv/csf/community-rules/snort.community','w')

	lines = oldConf.readlines()

	for line in lines:
		found = line.split()

		if len(found) > 1:
			if found[0] == 'alert' or found[1] == 'alert':
				line = line.split('#')

				if len(line) > 1:
					newConf.write(line[1][1:])
				else:
					newConf.write(line[0])

	oldConf.close()
	newConf.close()

	for ip in a:
	
		sftp = connSsh(ip).open_sftp()
		source = '/srv/csf/community-rules/snort.community'
		destination = '/etc/snort/rules/community.rules'
		sftp.put(source,destination)
		sftp.close()

	subprocess.call('rm -rf /srv/csf/community-rules',shell=True)
