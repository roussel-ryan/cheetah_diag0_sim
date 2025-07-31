#!/usr/bin/env bash

# Configures EPICS CA and PVA for use with Linac-Simulation-Server

# Channel access settings
export EPICS_CA_SERVER_PORT=10512
export EPICS_CA_ADDR_LIST=127.0.0.1
export EPICS_CA_AUTO_ADDR_LIST=NO

# PVA settings
export EPICS_PVA_SERVER_PORT=10513
export EPICS_PVA_ADDR_LIST=127.0.0.1
export EPCIS_PVA_AUTO_ADDR_LIST=YES

