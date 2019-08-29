import datetime

class OD_Check:

    def __init__(self, device_details, q, q_new_item, average):
        self.device_details = device_details
        self.device_setup = device_details['setup']
        self.q = q
        self.q_new_item = q_new_item
        self.outliers = 0
        self.average = average


    def set_od_bounds(self, min=None, max=None):

        if min != None:
            self.device_setup['min_OD'] = min
        if max != None:
            self.device_setup['max_OD'] = max

    def set_tolerance(self, lower, upper):

        if lower and upper:
            if lower <= upper:
                self.device_setup['lower_outlier_tol'] = lower
                self.device_setup['upper_outlier_tol'] = upper
                return ('Tolerances set to ' + lower + ' and ' + upper)
            else:
                return ('Invalid values')
        if lower and lower <= self.device_setup['upper_outlier_tol']:
            self.device_setup['lower_outlier_tol'] = lower
            return ('Tolerances set to ' + lower + ' and ' + self.device_setup['upper_outlier_tol'])
        if upper and upper >= self.device_setup['lower_outlier_tol']:
            self.device_setup['upper_outlier_tol'] = upper
            return ('Tolerances set to ' + self.device_setup['lower_outlier_tol'] + ' and ' + upper)
        return ('Ivalid input')

    def set_max_outliers(self, n):
        self.device_setup['max_outliers'] = n
        return ('Maximum number of outliers is ' + n)

    def stabilize(self, result):

        if not self.detect_outlier(result):
            cmd_id = 8
            pump_id = self.device_setup['pump_id']
            if result['od_1'][0] > self.device_setup['max_OD']:
                switch = True
            elif result['od_1'][0] < self.device_setup['min_OD']:
                switch = False
            else:
                return
            time_initiated = datetime.datetime.now()
            time_initiated = time_initiated.strftime("%m/%d/%Y, %H:%M:%S")
            self.q.put([time_initiated, '/'+self.device_details['node_number']+'/'+self.device_details['device_id'], cmd_id, [pump_id, switch]])


    def detect_outlier(self, result):

        if self.tolerance(self.device_setup['lower_outlier_tol']) > result['od_1'] > self.tolerance(self.device_setup['upper_outlier_tol']):
            self.outliers = 0
            result['od_1'] = (result['od_1'], False)
            return False
        else:
            self.outliers += 1
            if self.outliers > self.device_setup['max_outliers']:
                self.outliers = 0
                result['od_1'] = (result['od_1'], False)
                return False
            else:
                result['od_1'] = (result['od_1'], True)
                return True


    def tolerance(self, value):
        return ((100 + value) / 100) * self.average




