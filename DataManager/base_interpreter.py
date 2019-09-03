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
                break
            except Exception:
                count += 1
                sleep(2)

        if not result:
            raise Exception('Could not reach device')
        return result

    def execute(self, time_issued, target_address, id, args):
        try:
            result = self.device_con(id, args)
        except Exception as exc:
            result = str(exc)

        if id == 19 and not isinstance(result, str):
            self.OD_checker.stabilize(result)
        return (time_issued, target_address, id, args, result)