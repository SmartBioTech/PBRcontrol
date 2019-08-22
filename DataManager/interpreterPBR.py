from HWdevices import PBR_test

class InterpreterPBR:

    def __init__(self, device_details):
        self.device_details = device_details
        self.device = PBR_test.PBRtest(self.device_details['device_id'], self.device_details['address'])
        self.commands = {
                1: self.device.get_temp_settings,
                2: self.device.get_temp,
                3: self.device.set_temp,
                4: self.device.get_ph,
                5: self.device.measure_od,
                6: self.device.get_pump_params,
                7: self.device.set_pump_params,
                8: self.device.set_pump_state,
                9: self.device.get_light_intensity,
                10: self.device.set_light_intensity,
                11: self.device.turn_on_light,
                12: self.device.get_pwm_settings,
                13: self.device.set_pwm,
                14: self.device.get_o2,
                15: self.device.get_thermoregulator_settings,
                16: self.device.set_thermoregulator_state,
                17: self.device.measure_ft,
                18: self.device.get_co2,
                19: self.device.measure_all,
            }
