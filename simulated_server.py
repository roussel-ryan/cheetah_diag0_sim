from pcaspy import Driver, SimpleServer
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment, Screen
import torch
from utils.load_yaml import load_relevant_controls
from utils.pvdb import create_pvdb
from utils.beamline import create_beamline
import pprint
import numpy as np
import matplotlib.pyplot as plt
device_dict = load_relevant_controls('DL1.yaml')
#pprint.pprint(device_dict)
PVDB = create_pvdb(device_dict)
#pprint.pprint(PVDB)
sim_beamline = create_beamline(device_dict,screen_control_name='OTRS:IN20:571')

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

class CheetahBeamSimDriver(Driver):
    def __init__(self, particle_beam: ParticleBeam, beamline: Segment):
        super().__init__()
        #TODO: create particle beam here
        self.sim_beam = particle_beam
        #TODO: beamline here
        self.sim_beamline = beamline
        self.array_data = np.array([])

    def read(self,reason):
        if reason == 'OTRS:IN20:571:Image:ArrayData':
            screen_name = reason.rsplit(':',2)[0]
            print(f'reason is {reason}')
            self.array_data = self.get_screen_distribution(screen_name,
            particle_beam=self.sim_beam,beamline=self.sim_beamline)
            print(self.array_data.shape)
            value = list(self.array_data.flatten())
        elif 'QUAD' and 'BCTRL' in reason:
            print(f'reason is {reason}')
            value = self.getParam(reason)
            quad_name = reason.rsplit(':',1)[0]
            self.get_quad_value(quad_name, value, self.sim_beamline)
        else:
            value = self.getParam(reason)
        return value
        
    def write(self, reason, value):
        print(f'reason is {reason} with value: {value}')
        if 'QUAD' and 'BCTRL' in reason:
            quad_name = reason.rsplit(':',1)[0]
            print(quad_name)
            self.set_quad_value(quad_name,value,self.sim_beamline)
            self.setParam(reason,value)
        elif 'QUAD' in reason:
            self.setParam(reason,value)
        elif 'OTRS' in reason:
            print(f'reason is {reason}')
    
    def get_quad_value(self, quad_name:str, value:float,  beamline: Segment):
        #TODO: think about edge case when quad isn't in beamline what do we return?
        #TODO: probably don't need getter only need setter 
        names = [element.name for element in beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            quad_value = beamline.elements[index_num].k1.item()
            print(f'segment value = {quad_value}')
           

    def set_quad_value(self, quad_name:str, quad_value:float, beamline:Segment):
        ''' Takes quad ctrl name and sets value of PV and beamline elemet'''
        names = [element.name for element in beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            beamline.elements[index_num].k1 = torch.tensor(quad_value)


    def get_screen_distribution(self, screen_name:str, particle_beam: ParticleBeam, beamline:Segment )->list[float]:
        #TODO: put some safety stuff in here
        beamline.track(particle_beam)
        names = [element.name for element in beamline.elements]
        index_num = names.index(screen_name)
        img = beamline.elements[index_num].reading
        return img

    def plot_distribution(self):
        print(self.array_data.shape)
        plt.imshow(self.array_data)
        plt.show()

server = SimpleServer()
server.createPV('', PVDB)
driver = CheetahBeamSimDriver(particle_beam=sim_cheetah_beam, beamline=sim_beamline)
#
print('Starting simulated server')
while True:
    server.process(0.1)


#TODO: test functionality for getting and setting quads, for getting and setting Image:Arrays
#TODO: create framework for setting up beamline from device_dict, implement it for only one screen "OTR2"
#TODO: after setup param handling to be more robust
