from time import sleep

class BaseInterpreter:

    def device_con(self, id, args):
        args = eval(args)

        count = 0
        result = []
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

    def execute(self, time_issued, target_address, id, args, source):
        is_ok = True
        try:
            result = self.device_con(id, args)
        except Exception as exc:
            is_ok = False
            print(exc)
            result = str(exc)

        if not isinstance(result, str):
            if id == 19:
                self.OD_checker.stabilize(result)
            elif id == 8:
                self.OD_checker.change_pump_state(args[1])

        return (time_issued, target_address, id, args, (is_ok,result), source)