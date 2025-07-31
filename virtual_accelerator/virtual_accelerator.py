from cheetah.accelerator import Segment
from virtual_accelerator.pv_mapping import access_cheetah_attribute, get_pv_mad_mapping


class VirtualAccelerator:
    def __init__(self, lattice_file, mapping_file, initial_beam_distribution):
        self.lattice = Segment.from_lattice_json(lattice_file)
        self.mapping = get_pv_mad_mapping(mapping_file)
        self.initial_beam_distribution = initial_beam_distribution

        # do a first run to populate readings
        self.lattice.track(incoming=self.initial_beam_distribution)

    def set_pvs(self, values: dict):
        """
        Set the corresponding process variable (PV) to the given value on the virtual accelerator simulator.
        """

        for pv_name, value in values.items():
            # get the base pv name
            base_pv_name = ":".join(pv_name.split(":")[:3])
            attribute_name = ":".join(pv_name.split(":")[3:])

            # check if the pv_name is a control variable
            if base_pv_name in self.mapping:
                # set the value in the virtual accelerator simulator
                element = getattr(self.lattice, self.mapping[base_pv_name].lower())

                # if there are duplicate elements, just grab the first one (both will be adjusted)
                if isinstance(element, list):
                    element = element[0]

                try:
                    access_cheetah_attribute(element, attribute_name, value)
                except ValueError as e:
                    raise ValueError(f"Failed to set PV {pv_name}: {str(e)}") from e

            else:
                raise ValueError(f"Invalid PV base name: {base_pv_name}")

        # at the end of setting all PVs, run the simulation
        self.lattice.track(incoming=self.initial_beam_distribution)

    def get_pvs(self, pv_names: list):
        """
        Get the current value of the specified process variable (PV) from the virtual accelerator simulator.
        """

        values = {}
        for pv_name in pv_names:
            # get the base pv name
            base_pv_name = ":".join(pv_name.split(":")[:3])
            attribute_name = ":".join(pv_name.split(":")[3:])

            # check if the pv_name is a control variable
            if base_pv_name in self.mapping:
                element = getattr(self.lattice, self.mapping[base_pv_name].lower())

                # if there are duplicate elements, just grab the first one (both will be adjusted)
                if isinstance(element, list):
                    element = element[0]

                values[pv_name] = access_cheetah_attribute(element, attribute_name)
            else:
                raise ValueError(f"Invalid PV base name: {base_pv_name}")

        return values
