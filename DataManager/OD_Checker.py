import datetime

class OD_Check:
    def __init__(self, device_details, q, q_new_item):
        self.device_details = device_details
        self.q = q
        self.q_new_item = q_new_item
        self.outliers = 0
        self.average = False

    def change_od_bounds(self, min=None, max=None):
        if min != None:
            self.device_details['min_OD'] = min
        if max != None:
            self.device_details['max_OD'] = max

    def stabilize(self, OD):
        if not self.detect_outlier(OD):
            cmd_id = 8
            pump_id = self.device_details['pump_id']
            if OD > self.device_details['max_OD']:
                switch = True
            elif OD < self.device_details['min_OD']:
                switch = False
            else:
                return 'No action taken'
            time_initiated = datetime.datetime.now()
            time_initiated = time_initiated.strftime("%m/%d/%Y, %H:%M:%S")
            self.q.put(
                {
                'cmd_id' : cmd_id,
                'time_initiated' : time_initiated
                'args' : [pump_id, switch]
                })
            return 'Pumps set: ' + str(switch)

    def detect_outlier(self, OD):
        if self.tolerance(self.device_details['lower_outlier_tol']) > OD > self.tolerance(self.device_details['lower_outlier_tol']):
            self.outliers = 0
            return False
        else:
            self.outliers += 1
            if self.outliers > self.device_details['max_ouliers']:
                self.outliers = 0
                return False
            else:
                return True


    def tolerance(self):
        return ((100 + value) / 100) * self.average




