#!/usr/bin/python
# -*- coding: latin-1 -*-

from mod import *

##################################
# Mise à jour master cluster CSF #
##################################

fState = open('/srv/csf/script/state.conf','r')
state = fState.readline()

if state == 'CSF\n':
	majCsf(1)
elif state == 'BDD\n':
	majBdd()

fState.close()

#########################
# Mise à jour BDD SNORT #
#########################
majSnort(neighborsCsf())