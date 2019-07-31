from HWdevices import GAS_test as GAS, GMS_test as GMS, PBR_test as PBR

class Execute:
    """
    1-19  -> PBR
    20-27 -> GAS
    28-30 -> GMS

    """
    def run(self):

        return ((self.time_issued), self.id, self.args, self.commands[self.id](*self.args))


    def __init__(self, id,time_issued, args):
        self.time_issued = time_issued
        self.id = id
        self.args = args.split('/')
        self.commands = {
            1: PBR.PBRtest.get_temp_settings,
            2: PBR.PBRtest.get_temp,
            3: PBR.PBRtest.set_temp,
            4: PBR.PBRtest.get_ph,
            5: PBR.PBRtest.measure_od,
            6: PBR.PBRtest.get_pump_params,
            7: PBR.PBRtest.set_pump_params,
            8: PBR.PBRtest.set_pump_state,
            9: PBR.PBRtest.get_light_intensity,
            10: PBR.PBRtest.set_light_intensity,
            11: PBR.PBRtest.turn_on_light,
            12: PBR.PBRtest.get_pwm_settings,
            13: PBR.PBRtest.set_pwm,
            14: PBR.PBRtest.get_o2,
            15: PBR.PBRtest.get_thermoregulator_settings,
            16: PBR.PBRtest.set_thermoregulator_state,
            17: PBR.PBRtest.measure_ft,
            18: PBR.PBRtest.get_co2,
            19: PBR.PBRtest.measure_all,
            20: GAS.GAStest.get_co2_air,
            21: GAS.GAStest.get_small_valves,
            22: GAS.GAStest.get_flow,
            23: GAS.GAStest.get_flow_target,
            24: GAS.GAStest.set_flow_target,
            25: GAS.GAStest.get_flow_max,
            26: GAS.GAStest.get_pressure,
            27: GAS.GAStest.measure_all,
            28: GMS.GMStest.get_valve_flow,
            29: GMS.GMStest.set_valve_flow,
            30: GMS.GMStest.get_valve_info
        }