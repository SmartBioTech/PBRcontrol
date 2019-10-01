from time import sleep

class BaseInterpreter:

    def __init__(self, device_details, device_class, log):
        self.device_details = device_details
        self.log = log
        self.device = device_class(self.device_details['device_type'], self.device_details['address'])

    def device_con(self, id, args):
        args = eval(args)
        result=[]
        count = 0
        if not isinstance(id, int):
            raise Exception('Invalid Input')
        while count <= 5:
            try:
                result = self.commands[id](*args)
                return result
            except TypeError:
                raise Exception('Invalid input')
            except Exception:
                count += 1
                sleep(0.1)

        if not result:
            raise Exception('Could not reach device')
        return result

    def execute(self, time_issued, node_id, device_type, id, args, source):
        is_ok = True

        try:
            result = self.device_con(id, args)
        except Exception as exc:
            is_ok = False
            result = str(exc)

        if not isinstance(result, str):
            if id == 19:
                self.OD_checker.stabilize(result)


        return (time_issued, node_id, device_type, id, args, (is_ok,result), source)