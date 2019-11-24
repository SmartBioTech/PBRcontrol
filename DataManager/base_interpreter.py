from time import sleep
import datetime


class BaseInterpreter:

    def __init__(self, device_details, device_class, log):
        self.device_details = device_details
        self.log = log
        args = [self.device_details.get('device_id', self.device_details['device_type']),
                self.device_details.get('host_address')]

        if self.device_details['device_class'] == 'Phenometrics':
            args.append(self.device_details.get('host_port', 6161))
            args.append(self.device_details.get('encryption_key', 't2ih72c0husyrayh'))

        self.device = device_class(*args)

    def end(self):
        """
        Resolves loose ends before ending the device.

        :return: None
        """

        # if the device is a PBR, try to turn off the pump before ending. In case of problems, keep trying for
        # 3 minutes before giving up.
        if self.device_details['device_type'] == 'PBR':
            pump_id = self.device_details['setup']['pump_id']
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

                self.log.update_log(*response)  # log the change in pump state (or the cause of failure)

                # end the loop if the pump has been successfully turned off
                if result[0]:
                    break
                else:
                    counter += 1
                    sleep(3)

        self.device.disconnect()

    def device_con(self, id, args):
        """
        Method which connects to the device itself and executes the desired command

        :param id: int, ID of the command to issue
        :param args: list of arguments to pass with the command
        :return: response from the device
        """
        args = eval(args)
        result = []
        count = 0
        if not isinstance(id, int):
            raise Exception('Invalid Input')

        # in case of problems, keep trying 5 times
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
        """
        Prepare the command for execution and resolve special cases

        :param time_issued: UTC time
        :param node_id: int
        :param device_type: string
        :param command_id: int
        :param args: list of arguments
        :param source: string, 'external' if issued by BioArInEO, 'internal' if it was issued within PBRcontrol
        :return: tuple of loggable data
        """
        is_ok = True    # pre-set the state of result to ok
        try:
            # Phenometrics class must have individual pump management
            if self.device_details["device_class"] == "Phenometrics" and command_id == 8:
                if args[1]:     # if the pump is ot be turned on
                    self.pump_manager.start_pumping()   # let the devoted pump manager handle the pumping
                result = True   # describes that the command is being executed
            else:
                # connect to the device and execute the corresponding command
                result = self.device_con(command_id, str(args))

            # if the command was an instance of periodical measurement, stabilization must be executed
            if command_id == 19 and result[self.OD_checker.od_variant][0]:
                self.OD_checker.stabilize(result)
                if self.device_details["device_class"] == "Phenometrics":
                    self.pump_manager.last_OD = self.OD_checker.average
                    if self.pump_manager.last_OD != self.pump_manager.stored_OD:
                        self.pump_manager.od_changed.set()
        except Exception as exc:
            is_ok = False   # change the state of result to not ok
            result = str(exc)

        return time_issued, node_id, device_type, command_id, args, (is_ok, result), source
