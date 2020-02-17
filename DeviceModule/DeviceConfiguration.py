from DeviceModule.NodeConfiguration import NodeConfiguration


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

    def set_min_od(self, od: float):
        self.minOD = od

    def set_max_od(self, od: float):
        self.maxOD = od

    def set_od_bounds(self, min_od=None, max_od=None):
        if min_od is not None and max_od is not None:
            if min_od <= max_od:
                self.set_min_od(min_od)
                self.set_max_od(max_od)
            else:
                raise AttributeError("Minimal OD can't be smaller than Maximum OD")
        elif min_od is not None:
            if min_od <= self.maxOD:
                self.set_min_od(min_od)
        elif max_od is not None:
            if max_od >= self.minOD:
                self.set_max_od(max_od)
        else:
            raise AttributeError("Minimal OD can't be smaller than Maximum OD")

        return self.minOD, self.maxOD

    def set_lower_outlier_tol(self, tolerance: int):
        self.lowerOutlierTol = tolerance

    def set_upper_outlier_tol(self, tolerance: int):
        self.upperOutlierTol = tolerance

    def set_tolerance(self, lower=None, upper=None):
        """
        Changes the devices tolerance settings (lower/upper outlier tolerance). Check of validity of
        the requested values must be conducted as well - lower must be smaller then upper etc.

        :param lower: int
        :param upper: int
        :return the newly set tolerance values
        :raises Attribute error in case of invalid tolerance values
        """
        if lower is not None and upper is not None:
            if lower <= upper:
                self.set_lower_outlier_tol(lower)
                self.set_upper_outlier_tol(upper)
            else:
                raise AttributeError("Lower outlier tolerance must be smaller than Upper outlier tolerance")
        if lower is not None and lower <= self.upperOutlierTol:
            self.set_lower_outlier_tol(lower)

        elif upper is not None and upper >= self.lowerOutlierTol:
            self.set_upper_outlier_tol(upper)
        else:
            raise AttributeError("Lower outlier tolerance must be smaller than Upper outlier tolerance")

        return self.lowerOutlierTol, self.upperOutlierTol

    def set_max_outliers(self, max_outliers):
        self.maxOutliers = max_outliers
