from pcaspy import Driver, SimpleServer
import os
os.environ
class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()
        def read(self):
            pass
        def write(self):
            pass
        
server = SimpleServer()

PVDB = {
    'QUAD:DIAG0:330:BACT': {'value': 3.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:DIAG0:360:BACT': {'value': -4.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'QUAD:DIAG0:390:BACT': {'value': 8.0, 'prec': 5, 'hopr': 10, 'lopr': -10},
    'OTRS:DIAG0:420:Image:ArrayData': {'type': 'float', 'count': 600*800},
    'OTRS:DIAG0:420:Image:ArraySize1_RBV': {'value': 800, 'prec': 5, 'scan': 0},
    'OTRS:DIAG0:420:Image:ArraySize0_RBV': {'value': 600, 'prec': 5, 'scan': 0},
}

server.createPV('', PVDB)
driver = myDriver()

print('Starting simulated server')
while True:
    server.process(0.1)
