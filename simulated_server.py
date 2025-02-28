from pcaspy import SimpleServer
from cheetah.particles import ParticleBeam
from beamdriver import SimDriver
import torch
from utils.load_yaml import load_relevant_controls
from utils.pvdb import create_pvdb
from utils.beamline import create_beamline
import pprint

devices = load_relevant_controls('DL1.yaml')

screen_name = 'OTRS:IN20:571'
PVDB = create_pvdb(devices)
sim_beamline = create_beamline(devices,screen_name=screen_name)

pprint.pprint(devices)
#pprint.pprint(PVDB)

twiss_params = {
'energy' : torch.tensor(1e9),
'emittance_x' : torch.tensor(5e-8),
'emittance_y' : torch.tensor(5e-8),
'beta_x' : torch.tensor(1.0),
'alpha_x' : torch.tensor(0.0),
'beta_y' : torch.tensor(1.0),
'alpha_y' : torch.tensor(0.0),
'total_charge': torch.tensor(1e-9)
}
# set beam from random distribution not twiss

sim_cheetah_beam = ParticleBeam.from_twiss(**twiss_params)
server = SimpleServer()
server.createPV('', PVDB)
driver = SimDriver(particle_beam=sim_cheetah_beam, beamline=sim_beamline, screen=screen_name, devices=devices)

print('Starting simulated server')
while True:
    server.process(0.1)
