from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment, Screen
import torch

def create_beamline(device_dictionary:dict, screen_control_name:str, **params):

    segment_list = []
    keys = sorted([key for key in device_dictionary.keys()])
    for key_num, key in enumerate(keys):
        #z_pos = device_dictionary[key].get('metadata',{}).get('sum_l_meters', 'bad value')
    
        if 'QUAD' in key:
            l_eff = device_dictionary[key].get('metadata',{}).get('l_eff', .01)
            quad = Quadrupole(name = key, k1 = torch.tensor(0.0), length= torch.tensor(l_eff))
            drift = Drift(name = f'drift_{key_num}',length= torch.tensor(1.0))
            segment_list.append(quad)
            segment_list.append(drift)
        elif screen_control_name in key:
            screen =  Screen(name = key, resolution= (params.get('nrow', 600), params.get('ncol',800)), is_active=True )
    segment_list.append(screen)
    segment = Segment(elements = segment_list)
    print(segment.elements)
    return segment


    #TODO: remove elements from list that are not the camera we care about
    #TODO: filter on quads create quadrupole ensure typing is correct for length and k1
    #TODO: store in a list 
    #TODO: store z positions for quads in dict by name get differences add a drift that is the difference
