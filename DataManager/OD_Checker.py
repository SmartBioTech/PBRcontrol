import datetime
from collections import deque


class ODcheck:
    """
    Class implements methods used in regulation of density of the medium in a bioreactor by managing pump state
    """
    def __init__(self, device_details, q, q_new_item, average, pump_state):
        self.device_details = device_details
        self.device_setup = device_details['setup']
        self.q = q
        self.q_new_item = q_new_item
        self.outliers = 0
        self.average = average
        self.last_results = deque(maxlen=2)
        self.pump_state = pump_state
        self.od_variant = 'od_1' if self.device_setup['OD_channel'] == 1 else 'od_0'

    def change_pump_state(self, value):
        """
        Change pump state as the software sees it to True(on) or False(off)

        :param value: True for on, False for off
        """
        self.pump_state[0] = value

    def set_od_bounds(self, min, max):
        """
        Used to change the od bounds for given device, which are specified under the devices setup. Check of validity of
        the requested values must be conducted as well - min must be smaller then max etc.

        :raises: TypeError if the values provided are invalid
        :param min: float
        :param max: float
        :return: the newly set OD bounds
        """
        if min and max:
            if min <= max:
                self.device_setup['min_OD'] = min
                self.device_setup['max_OD'] = max
            else:
                raise TypeError("Minimal OD can't be smaller than Maximum OD")
        elif min:
            if min <= self.device_setup['max_OD']:
                self.device_setup['min_OD'] = min
        elif max:
            if max >= self.device_setup['min_OD']:
                self.device_setup['max_OD'] = max
        else:
            raise TypeError("Minimal OD can't be smaller than Maximum OD")
        return self.device_setup['min_OD'], self.device_setup['max_OD']

    def set_tolerance(self, lower, upper):
        """
        Changes the devices tolerance settings (lower/upper outlier tolerance). Check of validity of
        the requested values must be conducted as well - lower must be smaller then upper etc.

        :param lower: int
        :param upper: int
        :return: the newly set tolerance values
        """
        if lower and upper:
            if lower <= upper:
                self.device_setup['lower_outlier_tol'] = lower
                self.device_setup['upper_outlier_tol'] = upper
                return lower, upper
            else:
                raise TypeError("Lower outlier tolerance must be smaller than Upper outlier tolerance")
        if lower and lower <= self.device_setup['upper_outlier_tol']:
            self.device_setup['lower_outlier_tol'] = lower
            return lower, self.device_setup['upper_outlier_tol']
        if upper and upper >= self.device_setup['lower_outlier_tol']:
            self.device_setup['upper_outlier_tol'] = upper
            return self.device_setup['lower_outlier_tol'], upper
        raise TypeError("Lower outlier tolerance must be smaller than Upper outlier tolerance")

    def set_max_outliers(self, n):
        """
        Change the number of maximum outliers.

        :param n: int
        """

        self.device_setup['max_outliers'] = n
        return n

    def stabilize(self, result):
        """
        Sends the command to the device to turn the pump on/off if the measured value of OD is legit.

        :param result: measured OD in a dict
        """

        # add the measured OD value to most recently measured values of OD
        self.last_results.appendleft(result[self.od_variant][1])
        if not self.detect_outlier(result):     # check the validity of the value
            # set up the command for pump state change
            cmd_id = 8
            pump_id = self.device_setup['pump_id']

            # compare the value to max and min OD's and save the bool as switch - it tells us whether to turn the pump
            # on or off
            if result[self.od_variant][1][0] > self.device_setup['max_OD']:
                switch = True
            elif result[self.od_variant][1][0] < self.device_setup['min_OD']:
                switch = False
            else:
                return  # abort if the value is within acceptable range
            if switch == self.pump_state[0]:
                return  # abort if the pump is already in the state we would be turning it to

            # notify the program that the pump is going to be turned on to prevent the same command to be issued again
            self.change_pump_state(switch)

            # put the command in the device's queue
            time_initiated = datetime.datetime.utcnow()
            time_initiated = time_initiated.strftime("%Y-%m-%d %H:%M:%S")
            self.q.put((time_initiated,
                        str(self.device_details['node_id']),
                        self.device_details['device_type'],
                        cmd_id,
                        [pump_id, switch],
                        'internal'))
            self.q_new_item.set()

    def calculate_average(self):
        """
        Helper method which calculates the average of a list while removing the elements from the objects deque.

        :return: The average of the deque
        """
        my_list = []
        while self.last_results:
            my_list.append(self.last_results.pop())

        return sum(my_list)/len(my_list)

    def detect_outlier(self, result):
        """
        Decides whether the measured OD value is an outlier or not and saves it in the measured OD's dict.

        :param result: measured OD in a dict
        :return: True if it is an outlier, False otherwise
        """
        if self.tolerance(-self.device_setup['lower_outlier_tol']) <= result[self.od_variant][1] <= self.tolerance(self.device_setup['upper_outlier_tol']):
            self.outliers = 0
            self.average = self.calculate_average()
            result[self.od_variant] = (result[self.od_variant][0], (result[self.od_variant][1], False))
            return False
        else:
            self.outliers += 1
            if self.outliers > self.device_setup['max_outliers']:
                self.outliers = 0
                self.average = self.calculate_average()
                result[self.od_variant] = (result[self.od_variant][0], (result[self.od_variant][1], False))
                return False
            else:
                result[self.od_variant] = (result[self.od_variant][0], (result[self.od_variant][1], True))
                return True

    def tolerance(self, value):
        return ((100 + value) / 100) * self.average




