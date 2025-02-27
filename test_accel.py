
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment, Screen
import torch
import numpy as np
import matplotlib.pyplot as plt
#TODO: screen element inside of cheetah, pv returns histogram
#TODO: get default values for pvs
#TODO: hardcode all quads as beam line elements, hardcode PVDB for quads and camera, 
#

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

sim_cheetah_beam = ParticleBeam.from_twiss(**twiss_params)


sim_beamline = Segment(
    [    
        Drift(length=torch.tensor(1.0)),
#
    ]
)


tracked = sim_beamline.track(sim_cheetah_beam)
print(tracked.sigma_x)
#print(sim_beamline.OTRS2.get_read_beam().x)
names = [element.name for element in sim_beamline.elements]
print(names)
print(names.index('unnamed_element_0'))
sim_beamline.elements[0]
#plt.imshow(sim_beamline.OTRS2.reading)
#plt.show()
