class Device:
    def __init__(self, ID, address):
        self.ID = ID
        self.address = address

    def __str__(self):
        return self.ID + " @ " + str(self.address)

    def __repr__(self):
        return "VirtualDevice(" + self.ID + ", " + str(self.address) + ")"

    def disconnect(self):
        print('Test device ' + self.ID + ' is disconnecting')
