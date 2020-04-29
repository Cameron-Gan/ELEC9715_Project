from abc import abstractmethod, ABC


class Appliance:

    def __init__(self, max_load, maintain_load, max_level, min_level, ramp_up, ramp_down):
        self.max_load = max_load
        self.maintain_load = maintain_load
        self.max_level = max_level
        self.min_level = min_level
        self.ramp_up = ramp_up
        self.ramp_down = ramp_down

class HotWater(Appliance):

    def __init__(self, total_load, storage_time):
        super().__init__(total_load=total_load, storage_time=storage_time)


class AirConditioner(Appliance):

    def __init__(self, total_load, storage_time):
        super().__init__(total_load=total_load, storage_time=storage_time)


class PoolPump(Appliance):

    def __init__(self, total_load, storage_time):
        super().__init__(total_load=total_load, storage_time=storage_time)

