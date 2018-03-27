#!/usr/bin/python
# -*- coding: latin-1 -*-

from mod import *

##################################
# Mise à jour master cluster CSF #
##################################

fState = open('/srv/CSF/Script/state.conf','r')
state = fState.readline()

if state == 'CSF\n':
	majCsf()
elif state == 'BDD\n':
	majBdd()

fState.close()

#########################
# Mise à jour BDD SNORT #
#########################
majSnort(neighborsCsf)