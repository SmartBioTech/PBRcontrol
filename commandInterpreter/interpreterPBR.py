from DataManager import OD_Checker
from time import sleep
import datetime
from commandInterpreter import base_interpreter
import numpy as np
import threading


class DeviceManager(base_interpreter.BaseInterpreter):

    def initial_od(self):
        """
        Is executed when the device is initiated, provides information about the current state of OD in the PBR

        :return: float, average OD
        """
        data = []
        # collect the OD value from 5 measurements
        while len(data) < 5:
            try:
                data.append(self.device_con(5, '[1]'))
            except Exception as e:
                # in case of connection error, log it
                time_issued = datetime.datetime.utcnow()
                time_issued = time_issued.strftime("%Y-%m-%d %H:%M:%S")
                self.log.update_log(time_issued, self.device_details['node_id'], self.device_details['device_type'], 5, [], 'Waiting for connection...', 'internal')
                sleep(2)

        data.sort()
        computed = False

        # calculate the average OD from the measured data
        while not computed:

            mean = np.mean(data)
            median = np.median(data)

            if len(data) < 2:
                computed = True
                average = data[0]

            if mean / median <= 1:

                if mean / median >= 0.9:
                    computed = True
                    average = mean
                else:
                    data = data[1:]
            else:
                data = data[:-1]
        return average

    def __init__(self, device_details, q, q_new_item, log, device_class, experiment_details):
        self.q = q
        self.q_new_item = q_new_item
        self.pump_state = [False]
        self.log = log
        self.device_details = device_details
        self.device_class = device_class

        self.OD_checker = OD_Checker.ODcheck(device_details,
                                             self.q,
                                             self.q_new_item,
                                             0,
                                             self.pump_state)

        super(DeviceManager, self).__init__(self.device_details,
                                            self.device_class,
                                            self.log,
                                            self.pump_state,
                                            self.OD_checker,
                                            experiment_details)

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
            20: self.device.measure_AUX,
            21: self.device.flash_LED,
            22: self.device.get_hardware_address,
            23: self.device.get_cluster_name
        }

        try:
            self.device_con(8, str([device_details['setup']['pump_id'], False]))
        except Exception:
            pass
            # TODO: if there are problems with connection on initiation,
            #  conduct this info to BioArInEO and don't start the virtual device


        self.commands.update({
            24: self.OD_checker.set_max_outliers,
            25: self.OD_checker.set_od_bounds,
            26: self.OD_checker.set_tolerance
        }
        )

        initial_od = self.initial_od()
        self.OD_checker.average = initial_od

        if self.device_class == "Phenometrics":
            self.device.pump_manager.last_OD = initial_od
            self.device.pump_manager.stored_OD = initial_od

