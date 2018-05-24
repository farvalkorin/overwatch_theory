from copy import deepcopy
from overplay import Hero, Ability, run_simulation
from overplay.mccree import McCree

mc1_accuracy = 1.0
mc2_accuracy = 1.0

RANGE = 10

schedule1 = {}
primary_step = 0.3
current_time = 0.0
while current_time <= 5.0:
    schedule1[current_time] = [('primary', 1.0, RANGE,)]
    current_time += primary_step

if __name__ == '__main__':
    run_simulation(
        McCree,
        deepcopy(McCree),
        schedule1,
        {1.0: [('primary', mc1_accuracy, RANGE)],})

