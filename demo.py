from copy import deepcopy
from overplay import Hero, Ability, run_simulation
from overplay.mccree import McCree

mc1_accuracy = 0.2
mc2_accuracy = 0.2

RANGE = 10

schedule1 = {}
schedule2 = {}
primary_step = 510
current_time = 10
while current_time <= 10000:
    schedule1[current_time] = [('primary', mc1_accuracy, RANGE,)]
    schedule2[current_time + 200] = [('primary', mc2_accuracy, RANGE,)]
    current_time += primary_step

if __name__ == '__main__':
    run_simulation(
        McCree,
        deepcopy(McCree),
        schedule1,
        schedule2)

