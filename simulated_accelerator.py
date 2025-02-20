import torch
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment
import numpy as np
import matplotlib.pyplot as plt
import epics
#from simulated_server import PVDB

#particles = torch.distributions.MultivariateNormal(torch.zeros(7), torch.eye(7)*1e-6).rsample((10000,))
#beam_energy = torch.tensor(10e3)

import os

# Create the list of quads
Q = ["QUAD:DIAG0:330:BACT","QUAD:DIAG0:360:BACT","QUAD:DIAG0:390:BACT"]
IMAGE = 'OTRS:DIAG0:420:Image:ArrayData'

# create particle beam twiss parameters
energy = torch.tensor(1e9)  # Beam energy in eV (e.g., 1 GeV)
emittance_x = torch.tensor(5e-6)  # Horizontal emittance in m*rad (5 microns)
emittance_y = torch.tensor(5e-6)  # Vertical emittance in m*rad (5 microns)
beta_x = torch.tensor(10.0)  # Horizontal beta function in meters
alpha_x = torch.tensor(0.0) # Horizontal alpha
beta_y = torch.tensor(10.0)  # Vertical beta function in meters
alpha_y = torch.tensor(0.0)  # Vertical alpha



# Create the particle beam
incoming_beam = ParticleBeam.from_twiss(
    energy=energy,
    beta_x = beta_x, alpha_x = alpha_x, emittance_x = emittance_x,
    beta_y = beta_y, alpha_y = alpha_y, emittance_y = emittance_y)



sim_beamline = Segment(
    [
        Drift(length=torch.tensor(1.0)),
        Quadrupole(name="QUAD:DIAG0:330:BACT", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:DIAG0:360:BACT", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:DIAG0:390:BACT", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Drift(length=torch.tensor(1.0))
    ]
)

def update_quads(quad_list: list, beamline: Segment) -> Segment:
    '''Get the quad values through EPICS CA for quads and set the Segments quads to the epics value '''
    quads = {elem.name: elem for  elem in beamline.elements if isinstance(elem,Quadrupole)}
    print(f'Segment quad values before update: {quads}')
    for key, val in quads.items():
        if key in quad_list:
            quad_str = torch.tensor(epics.caget(key))
            val.k1 = quad_str

    print('\n')
    print(f'Segment quad values after update: {quads}')


def update_image(camera_pv, hist):
    flattened = list(hist.flatten())
    epics.caput(camera_pv,flattened)





#initial beam
tracked_beam = sim_beamline.track(incoming_beam)
xi_pos = tracked_beam.x.cpu().detach().numpy()
yi_pos = tracked_beam.y.cpu().detach().numpy()


hist_i, xi_edges, yi_edges = np.histogram2d(xi_pos, yi_pos, bins=(600,800))
update_image(IMAGE, hist_i)


update_quads(Q,sim_beamline)

#beam after adjusting quads
outgoing_beam = sim_beamline.track(tracked_beam)

x_pos = outgoing_beam.x.cpu().detach().numpy()
y_pos = outgoing_beam.y.cpu().detach().numpy()



hist, x_edges, y_edges = np.histogram2d(x_pos, y_pos, bins=(600,800))
update_image(IMAGE, hist)
print(type(hist))
difference = hist- hist_i

if np.all(difference==0):
    print('no difference.......')


fig, axs = plt.subplots(1,2, figsize=(8,4))
c1 = axs[0].imshow(hist_i.T, origin='lower', extent=[xi_edges[0], xi_edges[-1], yi_edges[0], yi_edges[-1]], aspect='auto')
axs[0].set_title('Initial Distribution')
c2 = axs[1].imshow(hist.T, origin='lower', extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]], aspect='auto')
axs[1].set_title('Distribution after quad changes')
fig.colorbar(c1,ax=axs[0])
fig.colorbar(c2,ax=axs[1])
plt.tight_layout()
plt.show()

