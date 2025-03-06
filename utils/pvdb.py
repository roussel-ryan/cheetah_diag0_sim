def create_pvdb(device: dict, **default_params) -> dict:
    #TODO: args is segme
    pvdb = {}

    for key, device_info in device.items():
        pvs = device_info.get('pvs', {})  # Safely get 'pvs' dictionary, default to empty dict
        
        if 'QUAD' in key:
            quad_pvdb = {
                pvs.get('bact', f'{key}:missing_bact'): {
                    'value': 0.0, 'prec': 5, 'hopr': 20, 'lopr': -20
                    },
                pvs.get('bctrl', f'{key}:missing_bctrl'): {
                    'value': 0.0, 'prec': 5, 'hopr': 20, 'lopr': -20
                    },
                pvs.get('bmax', f'{key}:missing_bmax'): {
                    'value': 20.0, 'prec': 5
                    },
                pvs.get('bmin', f'{key}:missing_bmin'): {
                    'value': -20.0, 'prec': 5
                    },
                pvs.get('bdes', f'{key}:missing_bdes'): {
                    'value': 0.0, 'prec': 5, 'hopr': 20, 'lopr': -20
                    },
                pvs.get('bcon', f'{key}:missing_bcon'): {
                    'value': 0.0, 'prec': 5, 'hopr': 20, 'lopr': -20
                    },
                pvs.get('ctrl', f'{key}:missing_ctrl'): {
                    'type':'enum', 'enums': ['Ready', 'TRIM', 'Perturb', 
                                            'MORE_IF_NEEDED']
                    # can freeze ctrls after caput bctrl and have a scan that procs after and resets the pv if needed
                    },
                
            }
            pvdb.update(quad_pvdb)

        elif 'OTRS' in key:
            screen_pvdb = {
                pvs.get('image', f'{key}:missing_image'): {
                    'type': 'float',
                    'count': default_params.get('n_row', 1392) * default_params.get('n_col', 1040)
                },
                pvs.get('n_row', f'{key}:missing_n_row'): {
                    'type': 'int',
                    'value': default_params.get('n_row', 1392)
                },
                pvs.get('n_col', f'{key}:missing_n_col'): {
                    'type': 'int',
                    'value': default_params.get('n_col', 1040)
                },
                pvs.get('resolution', f'{key}:missing_resolution'): {
                    'value': default_params.get('resolution', 12.5),
                    'unit': 'um/px'
                },
            }
            pvdb.update(screen_pvdb)

    return pvdb


#TODO: make defaults more robust
#TODO: ensure matching defaults are also passed to beamline.py correctly
#TODO: setup multiarea create_pvdb