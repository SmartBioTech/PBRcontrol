from virtual_devices.NodeConfiguration import NodeConfiguration


class DeviceConfiguration:

    def __init__(self, data: dict, nodeConfiguration: NodeConfiguration):
        self.nodeConfiguration = nodeConfiguration
        self.deviceType = data['device_type']
        self.deviceClass = data["device_class"]
        self.deviceName = str(nodeConfiguration.nodeId) + "-" + self.deviceClass + self.deviceType

        setup: dict = data.get('setup')
        if setup is not None:

            self.lowerOutlierTol = setup.get('lower_outlier_tol')
            self.upperOutlierTol = setup.get('upper_outlier_tol')
            self.maxOutliers = setup.get('max_outliers')
            self.minOD = setup.get('min_OD')
            self.maxOD = setup.get('max_OD')
            self.pumpId = setup.get('pump_id')
            self.ftChannel = setup.get('ft_channel')
            self.odChannel = setup.get('OD_channel')

        self.hostAddress = data.get('host_address')
        self.deviceId = data.get('device_id')
        self.encryptionKey = data.get('encryption_key')
        self.hostPort = data.get('host_port')