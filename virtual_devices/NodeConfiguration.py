class NodeConfiguration:

    def __init__(self, data: dict, node_id: int):
        self.nodeId = node_id
        self.sleepTime = data['sleep_time']
        self.rawDevicesData = data['devices']

