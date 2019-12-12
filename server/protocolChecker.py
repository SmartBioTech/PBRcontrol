class Protocol:
    node_keys = ['experiment_details', 'devices']

    experiment_keys = ['sleep_time']

    device_keys = ['device_type',
                   'device_class',
                   ]

    PBR_setup = ['lower_outlier_tol',
                 'upper_outlier_tol',
                 'max_outliers',
                 'min_OD',
                 'max_OD',
                 'pump_id',
                 'ft_channel',
                 'OD_channel',
                 'pump_on_outlier_tolerance_factor']

    phenometrics_keys = ['device_id',
                         'host_port',
                         'host_address',
                         'encryption_key']

    java_keys = ['host_address']

    device_variants = {'PSI_test': [],
                       'PSI_java': java_keys,
                       'Phenometrics': phenometrics_keys}

    def check_protocol(self, protocol):
        missing = []
        for node in protocol:
            for node_key in self.node_keys:
                if node_key not in protocol[node]:
                    missing.append("Node %s is missing %s. " % (node, node_key))

            for experiment_key in self.experiment_keys:
                if experiment_key not in protocol[node].get('experiment_details', {}):
                    missing.append("Node %s is missing %s in experiment_details. " % (node, experiment_key))

            device_counter = 0
            for device in protocol[node].get('devices', {}):

                for device_key in self.device_keys:
                    if device_key not in device:
                        missing.append(
                            "VirtualDevice %d on Node %s is missing %s. " % (device_counter, node, device_key))

                if 'device_type' in device and device['device_type'] == 'PBR':

                    for setup_key in self.PBR_setup:

                        if setup_key not in device.get('setup', {}):
                            if setup_key == 'pump_on_outlier_tolerance_factor' and device['class'] != 'Phenometrics':
                                continue
                            missing.append(
                                "PBR on Node %s is missing %s in its setup. " % (node, setup_key))
                if 'device_class' in device:
                    for key in self.device_variants[device['device_class']]:
                        if key not in device:
                            missing.append("VirtualDevice of %s is missing %s. " % (device['device_class'], key))
                device_counter += 1

        return missing
