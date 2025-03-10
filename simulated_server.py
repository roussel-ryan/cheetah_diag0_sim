from pcaspy import SimpleServer
from cheetah.particles import ParticleBeam
from beamdriver import SimDriver
from cheetah.accelerator import Segment 
import torch
from utils.load_yaml import load_relevant_controls
from utils.pvdb import create_pvdb
from utils.beamline import create_beamline
import pprint
'''
devices = load_relevant_controls('DL1.yaml')
pprint.pprint(devices)
screen_name = 'OTRS:IN20:571'
PVDB = create_pvdb(devices)
#print(PVDB.keys())
sim_beamline = create_beamline(devices,screen_name=screen_name)

#pprint.pprint(devices)
#pprint.pprint(PVDB)

twiss_params = {
'energy' : torch.tensor(1e9),
'emittance_x' : torch.tensor(5e-8),
'emittance_y' : torch.tensor(5e-8),
'beta_x' : torch.tensor(1.0),
'alpha_x' : torch.tensor(0.0),
'beta_y' : torch.tensor(1.0),
'alpha_y' : torch.tensor(0.0),
'total_charge': torch.tensor(1e5)
}
# set beam from random distribution not twiss

sim_cheetah_beam = ParticleBeam.from_twiss(**twiss_params)
server = SimpleServer()

server.createPV('', PVDB)
driver = SimDriver(particle_beam=sim_cheetah_beam, beamline=sim_beamline, screen=screen_name, devices=devices)

print('Starting simulated server')
while True:
    server.process(0.1)
'''
'''
design_incoming = ParticleBeam.from_twiss(
    beta_x=torch.tensor(4.682800510296777),
    alpha_x=torch.tensor(-1.796365384623861),
    emittance_x=torch.tensor(1e-06/264),
    beta_y=torch.tensor(4.688727673835899),
    alpha_y=torch.tensor(-1.7981430638316598),
    emittance_y=torch.tensor(1e-06/264),
    energy=torch.tensor(134999999.9999981),
    total_charge = torch.tensor(1e5),
    dtype=torch.float32,
)
'''
#print(design_incoming)
design_incoming = ParticleBeam.from_openpmd_file(path='impact_inj_output_YAG03.h5', energy = torch.tensor(125e6),dtype=torch.float32)
#TODO: pv that returns beam emittance 

lcls_lattice = Segment.from_lattice_json("lcls_cu_segment_otr2.json")

#print(lcls_lattice)

devices = load_relevant_controls('DL1.yaml')
screen_name = 'OTRS:IN20:571'
PVDB = create_pvdb(devices)
server = SimpleServer()

server.createPV('', PVDB)
print(design_incoming.emittance_x, design_incoming.emittance_y)
driver = SimDriver(particle_beam=design_incoming, beamline=lcls_lattice, screen=screen_name, devices=devices)

print('Starting simulated server')
while True:
    server.process(0.1)
