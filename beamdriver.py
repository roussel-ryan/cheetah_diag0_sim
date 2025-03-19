from pcaspy import Driver
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Segment
import numpy as np
import torch
from lcls_tools.common.data.model_general_calcs import bdes_to_kmod, kmod_to_bdes
from scipy.stats import cauchy
class SimDriver(Driver):
    def __init__(self, screen: str,
                 devices: dict,
                 design_incoming_beam:dict = None,
                 particle_beam: ParticleBeam = None,
                 lattice_file: str = None,
                 beamline: Segment = None):
        super().__init__()

        self.devices = devices
        self.screen = screen

        self._particle_beam = particle_beam
        self._design_incoming_beam = design_incoming_beam
        self._beamline = beamline
        self._lattice_file = lattice_file

        self.set_defaults_for_ctrl(0)

    def set_defaults_for_ctrl(self,default_value: int )->None:
        """Sets default quad ctrl value to ready state"""
        keys = [key for key in self.devices]
        for key in keys:
            if 'QUAD' in key:
                ctrl_pv = key + ":CTRL"
                self.setParam(ctrl_pv, default_value)

    @property
    def sim_beam(self) -> ParticleBeam:
        """Return the simulated beam, initializing if necessary."""
        if not hasattr(self, "_sim_beam") or hasattr(self,"_sim_beam") and self._sim_beam is None:
            if self._particle_beam:
                self._sim_beam = self._particle_beam
            elif self._design_incoming_beam:
                self._sim_beam = ParticleBeam.from_openpmd_file(**self._design_incoming_beam)
                self._sim_beam.particle_charges = torch.tensor(1.0)
            else:
                raise ValueError("Provide either a ParticleBeam instance or a beam configuration dictionary.")
        return self._sim_beam
    
    @sim_beam.setter
    def sim_beam(self,beam: ParticleBeam | None):
        """Sets sim_beam used by read and write functions,
        if set to None it will re-initialize to default value"""
        if not isinstance(beam, ParticleBeam):
            beam = None 
        self._sim_beam = beam

    @property
    def sim_beamline(self) -> Segment:
        """Return the beamline, initializing if necessary."""
        if not hasattr(self, "_sim_beamline") or hasattr(self,"_sim_beamline") and self._sim_beamline is None:
            if self._beamline:
                self._sim_beamline = self._beamline
            elif self._lattice_file:
                self._sim_beamline = Segment.from_lattice_json(self._lattice_file)
                self._sim_beamline.track(self.sim_beam)
            else:
                raise ValueError("Provide either a lattice file or a Segment instance.")
        return self._sim_beamline
    
    @sim_beamline.setter
    def sim_beamline(self,beamline: Segment | None):
        """Sets sim_beamline used by read and write functions,
        if set to None it will re-initialize to default value"""
        if not isinstance(beamline, Segment):
            beamline = None 
        self._sim_beamline = beamline

    @property
    def emittance_x(self) -> float:
        """Retrieve the horizontal beam emittance."""
        return self.sim_beam.emittance_x.item()

    @property
    def emittance_y(self) -> float:
        """Retrieve the vertical beam emittance."""
        return self.sim_beam.emittance_y.item()

    def reset_sim(self):
        """Resets sim_beam and sim_beamline to original state"""
        print('Resetting simulation')
        self.sim_beam = None
        self.sim_beamline = None


    def set_quad_value(self, quad_name: str, quad_value: float):
        """ Takes quad ctrl name and the k1 strength if the quad is in beamline"""
        names = [element.name for element in self.sim_beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            length = (self.sim_beamline.elements[index_num].length).item()
            energy = self.sim_beam.energy.item()
            kmod = bdes_to_kmod(e_tot=energy, effective_length=length, bdes = quad_value)
            self.sim_beamline.elements[index_num].k1 = torch.tensor(kmod)
            print(f"""Quad in segment with name {quad_name}
                   set to kmod {kmod} with quad value {quad_value}""")
            
    def get_quad_value(self, quad_name: str)-> float:
        """Retrieve quadrupole strength from the simulation beamline."""
        names = [element.name for element in self.sim_beamline.elements]
        if quad_name in names:
            index_num = names.index(quad_name)
            kmod = self.sim_beamline.elements[index_num].k1.item()
            length = self.sim_beamline.elements[index_num].length.item()
            energy = self.sim_beam.energy.item()
            quad_value = kmod_to_bdes(e_tot= energy, effective_length = length, k = kmod)
            print(f"kmod is {kmod} with quad_value {quad_value}")
        else:
            print(f"""Warning {quad_name} not in Segment""")
            quad_value = 0
        return quad_value


    def get_screen_distribution(self, screen_name: str)-> list[float]:
        """Retrieves image from simulation beamline and adds noise, has 
        a bug that the first time is called is not addding noise"""
        self.sim_beamline.track(self.sim_beam)
        names = [element.name for element in self.sim_beamline.elements]
        if screen_name in names:
            index_num = names.index(screen_name)
            image = self.sim_beamline.elements[index_num].reading
            image += np.abs(np.random.normal(loc=0, scale=10, size=image.shape))
            return image
        
    def read(self, reason):
        if 'Image:ArrayData' in reason and reason.rsplit(':',2)[0] == self.screen:
            print('reading screen')
            madname = self.devices[self.screen]["madname"]
            image_data = self.get_screen_distribution(screen_name = madname)
            value = image_data.flatten().tolist()
        elif 'QUAD' in reason and 'BCTRL' in reason or 'BACT' in reason:
            quad_name = reason.rsplit(':',1)[0]
            madname = self.devices[quad_name]["madname"]
            value = self.get_quad_value(madname)
        elif 'VIRT:BEAM:EMITTANCES' == reason:
            value = [self.sim_beam.emittance_x,self.sim_beam.emittance_y]
        else:
            value = self.getParam(reason)
        return value

    def write(self, reason, value):
        if 'QUAD' in reason and 'BCTRL' in reason:
            quad_name = reason.rsplit(':',1)[0]
            madname = self.devices[quad_name]["madname"]
            self.set_quad_value(madname,value)
        elif 'QUAD' in reason and 'BACT' in reason:
            pass
        elif 'QUAD' in reason:
            self.setParam(reason,value)
        elif 'OTRS' in reason:
            print(f"""Write to OTRS pvs is disabled, 
                  failed to write to {reason}""")
        elif 'VIRT:BEAM:RESET_SIM' == reason:
            self.reset_sim()
