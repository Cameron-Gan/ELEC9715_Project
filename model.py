from aCAT import Predispatch
from helperFunctions import convert_to_datetime
from appliance import Appliance
import pandas as pd
import numpy as np
from sys import float_info
from datetime import datetime, timedelta
import dateutil


class Node:
    def __init__(self, time):
        self.totalCost = float('nan')
        self.state_value = []
        self.path = []
        self.time = time


class Model:

    def __init__(self, start_percentage, n, app):
        self.n = 100
        self.start_n = start_percentage
        self.appliance = app
        self.predispatch = Predispatch().get_table('REGION_PRICE')
        self.predispatch = self.predispatch.loc[self.predispatch['REGIONID'] == 'NSW1']
        self.forecast_price = self.extract_forecast_price()
        self.time_steps = self.forecast_price.index.tolist()
        self.n_time_steps = len(self.forecast_price)
        self.cost = self.establish_costs()
        self.ramp_up = int(app.ramp_up * (app.max_level / (app.max_level - app.min_level)))
        self.ramp_down = int(app.ramp_down * (app.max_level / (app.max_level - app.min_level)))
        self.model_table = self.init_model_table()
        self.best_path = []

    def extract_forecast_price(self):
        price = self.predispatch.loc[:,['PERIODID', 'RRP']]
        price['RRP'] = price['RRP'].astype(float)
        price.PERIODID = price['PERIODID'].astype(int).apply(convert_to_datetime)
        price.set_index('PERIODID', inplace=True)
        return price

    def establish_costs(self):
        df = self.forecast_price.copy()
        df.rename(columns={'RRP': 'MaxLoadCost'}, inplace=True)
        df['MaxLoadCost'] = (df['MaxLoadCost'] / 1000) * self.appliance.max_load
        df['MaintainCost'] = (df['MaxLoadCost'] / 1000) * self.appliance.maintain_load
        return df.to_dict('index')

    def init_model_table(self):
        initial_time_step = []
        time = self.forecast_price.index[0] - timedelta(minutes=30)
        for i in range(0, self.n):
            initial_time_step.append(Node(time))
            if i == self.start_n:
                initial_time_step[i].totalCost = 0
                initial_time_step[i].state_value.append(self.start_n)
            initial_time_step[i].path.append(0)
        model_table = [initial_time_step]
        return model_table

    def model_time_step(self, time, model_table_index):
        time_step = []
        for i in range(0, self.n):
            # Here the previous index depending on the ramps are calculated flooring and ceiling them to n
            ramp_up_index = i - self.ramp_up if i - self.ramp_up >= 0 else 0
            ramp_down_index = i + self.ramp_down if i + self.ramp_down < self.n - 1 else self.n - 1
            maintain_index = i

            # print('ramp up '+str(ramp_up_index))
            # print('ramp down '+str(ramp_down_index))
            # print('maintain '+str(maintain_index))

            # this is a dictionary of the costs depending on the ramp. It should default to maintain.
            cost_dict = {ramp_up_index: self.cost[time]['MaxLoadCost'],
                         ramp_down_index: 0,
                         maintain_index: self.cost[time]['MaintainCost']}

            previous_time_step = self.model_table[model_table_index - 1]
            ramp_up_cost = cost_dict[ramp_up_index] + previous_time_step[ramp_up_index].totalCost
            ramp_down_cost = cost_dict[ramp_down_index] + previous_time_step[ramp_down_index].totalCost
            maintain_cost = cost_dict[maintain_index] + previous_time_step[maintain_index].totalCost

            ramp_up_cost = ramp_up_cost if not(np.isnan(ramp_up_cost)) else float_info.max
            ramp_down_cost = ramp_down_cost if not(np.isnan(ramp_down_cost)) else float_info.max
            maintain_cost = maintain_cost if not(np.isnan(maintain_cost)) else float_info.max

            # print(ramp_up_cost)
            # print(ramp_down_cost)
            # print(maintain_cost)

            new_node = Node(time)
            if ramp_up_cost < ramp_down_cost and ramp_up_cost < maintain_cost:
                new_node.totalCost = ramp_up_cost
                new_node.state_value.append(ramp_up_index)
                new_node.state_value = previous_time_step[ramp_up_index].state_value + new_node.state_value
                new_node.path.append(1)
                new_node.path = previous_time_step[ramp_up_index].path + new_node.path
            elif ramp_down_cost < ramp_up_cost and ramp_down_cost < maintain_cost:
                new_node.totalCost = ramp_down_cost
                new_node.state_value.append(ramp_down_index)
                new_node.state_value = previous_time_step[ramp_down_index].state_value + new_node.state_value
                new_node.path.append(0)
                new_node.path = previous_time_step[ramp_down_index].path + new_node.path
            elif maintain_cost < ramp_up_cost and maintain_cost < ramp_down_cost:
                new_node.totalCost = maintain_cost
                new_node.state_value.append(maintain_index)
                new_node.state_value = previous_time_step[maintain_index].state_value + new_node.state_value
                new_node.path.append(0.5)
                new_node.path = previous_time_step[maintain_index].path + new_node.path
            # print(new_node.path)
            time_step.append(new_node)
        # print(time)
        self.model_table.append(time_step)

    def run_model(self):
        for i in range(1, self.n_time_steps):
            # print(i)
            self.model_time_step(self.forecast_price.index[i], i)

    def get_cheapest_path(self):
        min = float_info.max
        min_index = 0
        for i in range(0, self.n):
            mnode = self.model_table[self.n_time_steps - 1][i]
            m = mnode.totalCost
            # print(m)
            # print(len(mnode.path))
            if m < min and len(mnode.path) == self.n_time_steps - 1:
                min_index = i
                min = m
        return self.model_table[self.n_time_steps - 1][min_index]


    # TODO return a path to a certain percentage
    def get_cheapest_path_to_level(self, p):
        self.appliance
        pass




if __name__ == '__main__':
    appliance = Appliance(100, 750, 100, 70, 5, 2)
    model = Model(90, 100, appliance)
    print(len(model.model_table[0]))
    # print(model.cost[dateutil.parser.isoparse('2020-04-29 15:30:00')]['MaintainCost'])
    model.run_model()
    print('finished')
    print(model.get_cheapest_path())


