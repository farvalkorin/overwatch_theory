import numpy as np
from numpy.random import rand, seed
import matplotlib.pyplot as plt

seed(123456)

# Brig Bashes, Melees, Whips
#   1 if the move used/hits in starting combo, 0 otherwise
#   If shield bash doesn't stun, whip might not hit
#   Melee accounted for automatically into simulation
combo_bash = 0
combo_whip = 0

# Soldier Parameters
biotic = False
sol_accuracy = 0.58
sol_crit_percent = 0.00

sol_dmg = 19
sol_rate = 9
sol_health = 200 - combo_bash * 50 - combo_whip * 70
print('Soldier Starting Health %d' % (sol_health,))
sol_armor = 0
sol_heal_rate = 40.8

brid_dmg = 35
brid_rate = 1/0.6
brid_health = 200
brid_armor = 50
brid_heal_rate = 16 # per second

time_res = 0.001
time = np.arange(0, 8, time_res)
sol_rng = rand(*time.shape)
sol_crit = rand(*time.shape)
# brid_rng = rand(*time.shape)

last_sold_shot = -9000
reload_time_start = -9000
last_brid_shot = 0

sol_shot_count = 0

soldier = np.zeros((len(time), 2,))
bridge = np.zeros((len(time), 2,))

for i in range(0, len(time)-1):
    current_time = time[i]
    if (current_time - last_sold_shot > (1.0 / sol_rate) and
        (current_time > 1.0 or (not combo_bash and not combo_whip))):
        # soldier shot attempt (rng accuracy)
        sol_shot_count += 1
        if sol_shot_count > 25:
            reload_time_start = current_time
            sol_shot_count = 0
            print('sol begins reload at %.2f' % (current_time,))
        elif sol_rng[i] < sol_accuracy and (current_time - reload_time_start) > 1.5:
            print('%.2f: soldier hits (%d shots) %.2f, %.2f' % (current_time, sol_shot_count, sol_rng[i], sol_accuracy,))
            if sol_crit[i] >= sol_crit_percent:
                sol_dmg = 19
            else:
                print('sol crits')
                sol_dmg = 19 * 2
            if brid_armor > 0:
                if sol_dmg > 10:
                    actual_dmg = int(sol_dmg - 5)
                else:
                    actual_dmg = int(sol_dmg / 2.0)
                brid_armor = brid_armor - actual_dmg
                if brid_armor < 0:
                    brid_health += brid_armor
                    brid_armor = 0
            else:
                actual_dmg = sol_dmg
                brid_health -= actual_dmg
        else:
            if (current_time - reload_time_start) > 1.5:
                print('%.2f: soldier misses' % current_time)
            else:
                print('%.2f: soldier reloading' % current_time)

        if reload_time_start != current_time:
            last_sold_shot = current_time

    bridge[i:, 0] = brid_health
    bridge[i:, 1] = brid_armor
    if brid_health <= 0:
        print('brid died')
        break

    if current_time - last_brid_shot > (1.0 / brid_rate):
        # bridge mace hits (100% accuracy)
        print('%.2f: brid hits' % current_time)
        if sol_armor > 0:
            if brid_dmg > 10:
                actual_dmg = int(brid_dmg - 5)
            else:
                actual_dmg = int(brid_dmg / 2.0)
            sol_armor -= actual_dmg
            if sol_armor < 0:
                sol_health += sol_armor
                sol_armor = 0
        else:
            actual_dmg = brid_dmg
            sol_health -= actual_dmg

        last_brid_shot = current_time

    soldier[i:, 0] = sol_health
    soldier[i:, 1] = sol_armor
    if sol_health <= 0:
        print('soldier died')
        break

    # healing :)
    if sol_health < 200:
        if biotic and (combo_bash or combo_whip) and 1.0 < current_time < 6.0:
            sol_heal_rate = 40.8 # biotic field active
        elif biotic and (not combo_bash and not combo_whip) and 0.0 < current_time < 5.0:
            sol_heal_rate = 40.8 # biotic field, no stun
        else:
            sol_heal_rate = 0.0
        sol_health += sol_heal_rate * time_res
    if brid_health + brid_armor < 250:
        brid_health += brid_heal_rate * time_res
        if brid_health > 200:
            diff = brid_health - 200
            brid_armor += diff
            brid_health = 200

plt.plot(time, soldier[:, 0] + soldier[:, 1], label='Total Soldier')
plt.plot(time, bridge[:, 0] + bridge[:, 1], label='Total Brigitte')
plt.plot(time, bridge[:, 0], label='Brigitte Health Only')
plt.plot(time, 120 * np.ones(time.shape), label='Helix Dmg Limit')
if combo_bash and combo_whip:
    plt.title('Full Brigitte Combo, Soldier Stun, Biotic %s, %.2f acc %.2f crit' % (
        biotic, sol_accuracy, sol_crit_percent,))
elif combo_bash:
    plt.title('Brigitte Bash Start, Soldier Stun, Biotic %s, %.2f acc %.2f crit' % (
        biotic, sol_accuracy, sol_crit_percent,))
elif combo_whip:
    plt.title('Brigitte Whip Start, Soldier Stun, Biotic %s, %.2f acc %.2f crit' % (
        biotic, sol_accuracy, sol_crit_percent,))
else:
    plt.title('Brigitte Melee Only, Soldier No Stun, Biotic %s, %.2f acc %.2f crit' % (
        biotic, sol_accuracy, sol_crit_percent,))

plt.legend()
plt.show()