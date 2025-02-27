from cheetah.particles import ParticleBeam
from cheetah.accelerator import Drift, Quadrupole, Segment, Screen
import torch

def create_beamline(device_dictionary:dict):
    keys = [key for key in device_dictionary.keys()]
    print(keys)
    print(keys.sort())
    