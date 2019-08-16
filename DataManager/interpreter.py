from DataManager import experiment_settings

class Interpreter:
    """
    1-19  -> PBR
    20-27 -> GAS
    28-30 -> GMS

    """
    def reset_measurement(self, t):
        self.device_details['measurement_interval'] = t


    def execute(self, time_issued, id, args):
        if args == '':
            args = None

        if args != None:
            args = args.split('/')
            for i in range(len(args)):
                try:
                    args[i] = int(args[i])
                except TypeError:
                    if args[i] == 'True':
                        args[i] = True
                    elif args[i] == False:
                        args[i] = False

            result = self.commands[id](*args)

        else:
            result = self.commands[id]()

        return (time_issued, id, args, result)



    def __init__(self, device_details, q, q_new_item):
        self.q = q
        self.q_new_item = q_new_item
        self.devtype = device_details['type']
        self.device_details = device_details
        self.measurement = experiment_settings.PeriodicalMeasurement(self.q, self.q_new_item,
                                                                     self.device_details, self.devtype)
        self.measurement.start()

        if self.device_details['test'] == True:

            exec('from HWdevices.' + self.devtype + '_test import ' + self.devtype + 'test')
            self.devtype += 'test'

        else:
            exec('from HWdevices.' + devtype + ' import ' + devtype)

        self.device = eval(self.devtype)(self.device_details['id'], self.device_details['address'])
        self.commands = {
            0 : self.reset_measurement
        }

        if 'PBR' in self.devtype:
            self.commands.update({
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
            })


        elif 'GAS' in self.devtype:
            self.commands.update({
                20: self.device.get_co2_air,
                21: self.device.get_small_valves,
                22: self.device.get_flow,
                23: self.device.get_flow_target,
                24: self.device.set_flow_target,
                25: self.device.get_flow_max,
                26: self.device.get_pressure,
                27: self.device.measure_all,
            })


        elif 'GMS' in self.devtype:
            self.commands.update({
                28: self.device.get_valve_flow,
                29: self.device.set_valve_flow,
                30: self.device.get_valve_info
            })
