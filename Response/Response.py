from DeviceModule.Command import Command
from utils.TimeStamper import TimeString
from DeviceModule.DeviceConfiguration import DeviceConfiguration


class Response:

    def __init__(self,
                 command: Command,
                 deviceConfig: DeviceConfiguration,
                 response):

        self.source = command.source
        self.time_executed = TimeString.now()
        self.target_arguments = command.args
        self.command_id = command.command_id
        self.device_class = deviceConfig.deviceClass
        self.device_type = deviceConfig.deviceType
        self.node_id = deviceConfig.nodeConfiguration.nodeId
        self.time_issued = command.time_issued
        self.response: MeasureAllResponse = response


class MeasureAllResponse:

    def __init__(self, is_valid):
        self.is_valid: bool = is_valid


class PBRMeasureAllResponse(MeasureAllResponse):

    def __init__(self, is_valid, response):
        super(PBRMeasureAllResponse).__init__(is_valid)

        self.pwm_settings = response.get('pwm_settings')
        self.light_0 = response.get('light_0')
        self.light_1 = response.get('light_1')
        self.od_0 = response.get('od_0')
        self.od_1 = response.get('od_1')
        self.ph = response.get('ph')
        self.temp = response.get('temp')
        self.pump = response.get('pump')
        self.o2 = response.get('o2')
        self.co2 = response.get('co2')
        self.ft = response.get('ft')


class GASMeasureAllResponse(MeasureAllResponse):

    def __init__(self, is_valid, response):
        super(GASMeasureAllResponse).__init__(is_valid)

        self.co2_air = response.get('co2_air')
        self.flow = response.get('flow')
        self.pressure = response.get('pressure')
