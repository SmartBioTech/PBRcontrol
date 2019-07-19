class Device:
    def __init__(self, ID, address):
        self.ID = ID
        self.address = address

    def __str__(self):
        return self.ID + " @ " + str(self.address)

    def __repr__(self):
        return "Device(" + self.ID + ", " + str(self.address) + ")"
