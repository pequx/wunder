class Spread(object):
    __slots__ = ["timestamp", "value_1", "value_2", "value_3", "value_4"]

    def __init__(self, timestamp, value_1, value_2, value_3, value_4):
        self.timestamp = timestamp
        self.value_1 = value_1
        self.value_2 = value_2
        self.value_3 = value_3
        self.value_4 = value_4

    def get(self, slot):
        return self.__getattribute__(slot)
