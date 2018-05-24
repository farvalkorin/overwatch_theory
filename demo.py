from copy import deepcopy
from overplay import Hero, Ability, run_simulation
from overplay.mccree import McCree

if __name__ == '__main__':
    run_simulation(
        McCree,
        deepcopy(McCree),
        {0.0: ['primary'],},
        {1.0, ['primary'],})

