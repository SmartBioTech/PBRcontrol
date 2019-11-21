from DataManager import OD_Checker
from time import sleep
import datetime
from DataManager import base_interpreter
import numpy as np
import threading


class DeviceManager(base_interpreter.BaseInterpreter):

    def initial_od(self):
        data = []
        while len(data) < 5:
            try:
                data.append(self.device_con(5, '[1]'))
            except Exception:
                time_issued = datetime.datetime.utcnow()
                time_issued = time_issued.strftime("%m-%d-%Y %H:%M:%S")
                address = '/' + str(self.device_details['node']) + '/' + str(self.device_details['device_id'])
                self.log.update_log(time_issued, address, 5, [], 'Waiting for connection...')
                sleep(2)

        data.sort()
        computed = False

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

    def __init__(self, device_details, q, q_new_item, log, device_class, experimental_details):
        self.q = q
        self.q_new_item = q_new_item
        super(DeviceManager, self).__init__(device_details, device_class, log)
        self.device.set_pump_state(device_details['setup']['pump_id'], False)
        self.pump_state = [False]
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

        self.OD_checker = OD_Checker.ODcheck(self.device_details,
                                             self.q,
                                             self.q_new_item,
                                             self.initial_od(),
                                             self.pump_state)

        self.commands.update({
            24: self.OD_checker.set_max_outliers,
            25: self.OD_checker.set_od_bounds,
            26: self.OD_checker.set_tolerance
        }
        )

        self.pump_manager = PhenometricsPumpManager(self.pump_state, self.device, self.device_details, self.log,
                                                    self.OD_checker.average, experimental_details)
        self.pump_manager.start()


class PhenometricsPumpManager(threading.Thread):
    def __init__(self, pump_state, device, device_details, log, last_OD, experimental_details):
        super(PhenometricsPumpManager, self).__init__(daemon=True)
        self.pump_state = pump_state
        self.device = device
        self.log = log
        self.device_details = device_details
        self.last_OD = last_OD
        self.stored_OD = last_OD
        self.stop_request = threading.Event()
        self.start_pumping_event = threading.Event()
        self.od_changed = threading.Event()
        self.wait_time = experimental_details['sleep_time']

    def run(self):
        self.start_pumping_event.wait()
        while not self.stop_request.isSet():
            self.start_pumping_event.clear()

            self.device_details['setup']['lower_outlier_tol'] *= 2
            self.device_details['setup']['upper_outlier_tol'] *= 2

            self.pump_state[0] = True  # is this necessary?
            print("Log pump on")

            while self.last_OD > self.device_details["setup"]["min_OD"]:
                self.od_changed.clear()
                self.stored_OD = self.last_OD
                print("Turning on pump...")
                try:
                    # this turns on the pump (works only if the pump goes from 0 to 1)
                    self.device.connection.send_command(self.device.ID, 'setAux2', [1])
                    # sleep 20 seconds, should be enough to accomplish steps 1. and 2.
                    sleep(2)
                    # reset the pump to zero state that is necessary for success of next set of the pump
                    self.device.connection.send_command(self.device.ID, 'setAux2', [0])
                except Exception:
                    continue
                self.od_changed.wait()  # we wait until OD has changed

            self.pump_state[0] = False  # is this necessary?

            self.device_details['setup']['lower_outlier_tol'] /= 2
            self.device_details['setup']['upper_outlier_tol'] /= 2

            print("Log pump off")
            self.start_pumping_event.wait()

    def start_pumping(self):
        self.start_pumping_event.set()

    def log_pump_change(self, state):
        time_issued = (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        node_id = self.device_details["node_id"]
        device_type = self.device_details["device_type"]
        command_id = 8
        args = [self.device_details['setup']['pump_id'], state]
        self.log.update_log(time_issued, node_id, device_type, command_id, args, (True, True), "internal")

    def exit(self):
        self.stop_request.set()
