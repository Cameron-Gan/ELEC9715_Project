

number_of_states
future_steps

table_size = future_steps * number_of_states

load

cost = load * price

start_state

decline_rate

incline_rate

max_state

min_state

class node:
    def __init__(self, state_value):
        self.state_value = state_value
        self.cost = -1
        self.prev_node = None



dynamic_forward_table = []
initial_state = []
for i in range(0, number_of_states):
    n = node(i)
    if i == start_state:
        n.cost = 0
    initial_state.append(n)

dynamic_forward_table.append(initial_state)

for i in range(0,future_steps):
    for elem in dynamic_forward_table[i]:
        if elem.cost <= 0:

