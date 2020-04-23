from abc import abstractmethod, ABC


class Appliance:

    def __init__(self, total_load, storage_time, storage_fill_rate):
        self.total_load = total_load
        self.storage_time = storage_time


class HotWater(Appliance):

    def __init__(self, total_load, storage_time):
        super().__init__(total_load=total_load, storage_time=storage_time)


class AirConditioner(Appliance):

    def __init__(self, total_load, storage_time, required_on_time):
        super().__init__(total_load=total_load, storage_time=storage_time)
        self.required_on_time = required_on_time


class PoolPump(Appliance):

    def __init__(self, total_load, storage_time, required_duration):
        super().__init__(total_load=total_load, storage_time=storage_time)
        self.required_duration = required_duration

