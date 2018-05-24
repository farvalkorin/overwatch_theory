from copy import deepcopy
from overplay import Hero, Ability, run_simulation
from overplay.mccree import McCree

mc1_accuracy = 1.0
mc2_accuracy = 1.0

RANGE = 10

if __name__ == '__main__':
    run_simulation(
        McCree,
        deepcopy(McCree),
        {0.0: [('primary', mc1_accuracy, RANGE)],},
        {1.0: [('primary', mc1_accuracy, RANGE)],})

