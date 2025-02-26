from pcaspy import Driver, SimpleServer
from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment, Screen
import torch
from utils.load_yaml import load_relevant_controls
from utils.pvdb import create_pvdb
from utils.beamline import create_beamline

device_dict = load_relevant_controls('DL1.yaml')
pvdb = create_pvdb(device_dict)
sim_beamline = create_beamline(device_dict)

twiss_params = {
'energy' : torch.tensor(1e9),
'emittance_x' : torch.tensor(5e-6),
'emittance_y' : torch.tensor(5e-6),
'beta_x' : torch.tensor(10.0),
'alpha_x' : torch.tensor(0.0),
'beta_y' : torch.tensor(10.0),
'alpha_y' : torch.tensor(0.0),
'total_charge': torch.tensor(1e-9)
}

sim_cheetah_beam = ParticleBeam.from_twiss(**twiss_params)


sim_beamline = Segment(
    [
        Drift(length=torch.tensor(1.0)),
        Quadrupole(name="QUAD:IN20:425", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:IN20:511", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:IN20:571", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:IN20:631", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),
        Quadrupole(name="QUAD:IN20:651", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),     
        Quadrupole(name="QUAD:IN20:771", k1 = torch.tensor(1.0), length=torch.tensor(0.1)),     
        Drift(length=torch.tensor(1.0)),
        Screen(name='OTR02', pixel_size=torch.ones(2)*(10e-6), is_active=True)
    ]
)

class CheetahBeamSimDriver(Driver):
    def __init__(self, particle_beam: ParticleBeam, beamline: Segment):
        super().__init__()
        #TODO: create particle beam here
        self.sim_beam = particle_beam
        #TODO: beamline here
        self.sim_beamline = beamline

    def read(self,reason):
        if reason == 'OTRS:IN20:571:Image:ArrayData':
            print(f'reason is {reason}')
            value = self.getParam(reason)
        elif 'QUAD' and 'BACT' in reason:
            print(f'reason is {reason}')
            value = self.getParam(reason)
            quad_name = reason.rsplit(':',1)[0]

            self.get_quad_value(quad_name, value, self.sim_beamline)
        else:
            value = self.getParam(reason)
        return value
        #TODO: read only images, self.beamline.track() ->hist 
        
    def write(self, reason, value):
        print(f'reason is {reason} with value: {value}')
        if 'QUAD' and 'BACT' in reason:
            quad_name = reason.rsplit(':',1)[0]
            print(quad_name)
            self.set_quad_value(quad_name,value,self.sim_beamline)
            self.setParam(reason,value)
    
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

server = SimpleServer()
PVDB = {
    'QUAD:IN20:425:BACT': {'value': 3.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:IN20:511:BACT': {'value': -4.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:IN20:571:BACT': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:IN20:631:BACT': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:IN20:651:BACT': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:IN20:771:BACT': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'OTRS:IN20:571:Image:ArrayData': {'type': 'float', 'count': 1392*1040},
    'OTRS:IN20:571:Image:ArraySize1_RBV': {'value': 1392, 'prec': 5, 'scan': 0},
    'OTRS:IN20:571:Image:ArraySize0_RBV': {'value': 1040, 'prec': 5, 'scan': 0},
    'OTRS:IN20:571:Image:ArrayRate_RBV' : {'value': 4.0, 'prec':2, 'scan':0},
    #'QUADSEGMENTVALUES': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
}

server.createPV('', PVDB)
driver = CheetahBeamSimDriver(particle_beam=sim_cheetah_beam, beamline=sim_beamline)

print('Starting simulated server')
while True:
    server.process(0.1)

    '''
    def get_image_array(self, screen_name:str, particle_beam: ParticleBeam, beamline: Segment, nrows: int, ncols:int):
        print(screen_name)
        tracked_beam = beamline.track(particle_beam)
        x_pos = tracked_beam.x.cpu().detach().numpy()
        y_pos = tracked_beam.y.cpu().detach().numpy()
        hist, x_edges, y_edges = np.histogram2d(x_pos, y_pos, bins=(nrows,ncols))
        flat_hist = list(hist.flatten())
        return flat_hist
    '''
