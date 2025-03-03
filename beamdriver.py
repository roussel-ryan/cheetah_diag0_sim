from pcaspy import Driver
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Segment
import numpy as np
import torch

class SimDriver(Driver):
    def __init__(self, particle_beam: ParticleBeam, beamline: Segment, screen: str, devices: dict):
        super().__init__()
        self.devices = devices
        self.sim_beam = particle_beam
        self.sim_beamline = beamline
        self.image_data = np.array([])
        self.screen = screen

    def read(self,reason):
        if 'Image:ArrayData' in reason and reason.rsplit(':',2)[0] == self.screen:
            madname = self.devices[self.screen]["madname"]
            print(madname)
            self.image_data = self.get_screen_distribution(screen_name = madname,
            particle_beam=self.sim_beam,beamline=self.sim_beamline)
            value = list(self.image_data.flatten())
        elif 'QUAD' and 'BCTRL' in reason:
            quad_name = reason.rsplit(':',1)[0]
            madname = self.devices[quad_name]["madname"]
            value_from_segment = self.get_quad_value(madname, self.sim_beamline)
            value = self.getParam(reason)
            print(f"""segment value for {madname}  {value_from_segment},
            matches pv value: {value}, {value_from_segment==value}""")
        else:
            value = self.getParam(reason)
        return value
        
    def write(self, reason, value):
        if 'QUAD' and 'BCTRL' in reason:
            quad_name = reason.rsplit(':',1)[0]
            madname = self.devices[quad_name]["madname"]
            print(madname)
            self.set_quad_value(madname,value,self.sim_beamline)
            self.setParam(reason,value)
        elif 'QUAD' in reason:
            self.setParam(reason,value)
        elif 'OTRS' in reason:
            print(f"""Write to OTRS pvs is disabled, 
                  failed to write to {reason}""")
    
    def get_quad_value(self, quad_name:str, beamline: Segment):
        names = [element.name for element in beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            quad_value = beamline.elements[index_num].k1.item()
        else:
            print(f"""Warning {quad_name} not in Segment""")
            quad_value = np.nan
        return quad_value

    def set_quad_value(self, quad_name:str, quad_value:float, beamline:Segment):
        ''' Takes quad ctrl name and the k1 strength if the quad is in beamline'''
        names = [element.name for element in beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            beamline.elements[index_num].k1 = torch.tensor(quad_value)
            print(f"""Quad in segment with name {quad_name}
                   set to {quad_value}""")

    def get_screen_distribution(self, screen_name:str, particle_beam: ParticleBeam, beamline:Segment )->list[float]:
        #TODO: put some safety stuff in here
        beamline.track(particle_beam)
        names = [element.name for element in beamline.elements]
        if screen_name in names:
            index_num = names.index(screen_name)
            img = beamline.elements[index_num].reading
            return img
        
#TODO: start server takebeam size measurements and plot them in experiment.nb - image isn't processing
#TODO: build cheetah accelerator with madname instead of control name -> done I think? 
#TODO: when a bctrl or image pv is called look up the pv in the accelerator by madname

#TODO: build in wait_time when performing scans
#TODO: when caput to bctrl -> set bact pv,