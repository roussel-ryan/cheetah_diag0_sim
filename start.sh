#!/usr/bin/env bash

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

# If the particle distribution has not been extracted, extract it now
[ ! -f h5/impact_inj_output_YAG03.h5 ] && echo "Extracting YAG03 h5..." && xz -k -d h5/impact_inj_output_YAG03.h5.xz

# Get into the rhel7 env
source /afs/slac/g/lcls/package/anaconda/envs/rhel7_devel/bin/activate

# Setup epics vars
source epics-env.sh

# Start it
echo "Starting server..."
python3 simulated_server.py
