from pcaspy import SimpleServer
from cheetah.particles import ParticleBeam
from beamdriver import SimDriver
from cheetah.accelerator import Segment 
import torch
from utils.load_yaml import load_relevant_controls
from utils.pvdb import create_pvdb

#design_incoming = ParticleBeam.from_openpmd_file(path='impact_inj_output_YAG03.h5', energy = torch.tensor(125e6),dtype=torch.float32)
#lcls_lattice = Segment.from_lattice_json("lcls_cu_segment_otr2.json")
design_incoming_beam = {'path': 'impact_inj_output_YAG03.h5',
                         'energy': torch.tensor(125e6),
                         'dtype':torch.float32}
lcls_lattice = 'lcls_cu_segment_otr2.json'
devices = load_relevant_controls('DL1.yaml')
screen_name = 'OTRS:IN20:571'
PVDB = create_pvdb(devices)
custom_pvs = {'VIRT:BEAM:EMITTANCES': {'type':'float', 'count': 2},
              'VIRT:BEAM:RESET_SIM': {'value': 0}   
}
PVDB.update(custom_pvs)
server = SimpleServer()
server.createPV('', PVDB)
driver = SimDriver(screen=screen_name,
                   devices=devices,
                   design_incoming_beam=design_incoming_beam,
                   lattice_file=lcls_lattice)

print('Starting simulated server')
while True:
    server.process(0.1)
