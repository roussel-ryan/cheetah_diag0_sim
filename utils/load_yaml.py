import yaml
import pprint
import yaml

def load_relevant_controls(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    relevant_controls = {}
    
    # Process magnets
    for name, info in data.get('magnets', {}).items():
        if info['metadata']['type'] == 'QUAD':
            control_name = info['controls_information']['control_name']
            relevant_controls[control_name] = {}
            relevant_controls[control_name]['pvs'] = info['controls_information']['PVs']
            relevant_controls[control_name]['metadata'] = info['metadata']
    
    # Process screens
    for name, info in data.get('screens', {}).items():
        if info['metadata']['type'] == 'PROF':  # Assuming 'PROF' represents OTR
            control_name = info['controls_information']['control_name']
            relevant_controls[control_name] = {}
            relevant_controls[control_name]['pvs'] = info['controls_information']['PVs']
            relevant_controls[control_name]['metadata'] = info['metadata']
    return relevant_controls

# Example usage
#yaml_file = "DL1.yaml"  # Replace with actual path
#controls_dict = load_relevant_controls(yaml_file)
#pprint.pprint(controls_dict)
