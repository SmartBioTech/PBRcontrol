from time import sleep
import datetime


class BaseInterpreter:

    def __init__(self, device_details, device_class, log):
        self.device_details = device_details
        self.log = log
        args = [self.device_details.get('device_id', self.device_details['device_type']),
                self.device_details.get('address', 'localhost')]

        if self.device_details['device_class'] == 'Phenometrics':
            args.append(self.device_details.get('host_port', 6161))
            args.append(self.device_details.get('encryption_key', 't2ih72c0husyrayh'))

        self.device = device_class(*args)

    def end(self):
        pump_id = self.device_details['setup']['pump_id']
        if self.device_details['device_type'] == 'PBR':
            counter = 0
            while counter < 60:
                try:
                    result = True, self.device.set_pump_state(pump_id, False)
                except Exception as e:
                    result = False, e

                response = [(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                            self.device_details['node_id'],
                            self.device_details['device_type'],
                            8,
                            [pump_id, False],
                            result,
                            'internal']

                self.log.update_log(*response)
                if result[0]:
                    break
                else:
                    counter += 1
                    sleep(3)

        self.device.disconnect()

    def device_con(self, id, args):
        args = eval(args)
        result = []
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

    def execute(self, time_issued, node_id, device_type, command_id, args, source):
        is_ok = True
        try:
            if self.device_details["device_class"] == "Phenometrics" and command_id == 8:
                if args[1]:
                    self.pump_manager.pump_on()
                result = True
            else:
                result = self.device_con(command_id, args)
            if command_id == 19 and result['od_1'][0]:
                self.OD_checker.stabilize(result)
        except Exception as exc:
            is_ok = False
            result = str(exc)

        return time_issued, node_id, device_type, command_id, args, (is_ok, result), source
