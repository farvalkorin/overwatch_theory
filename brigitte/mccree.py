import numpy as np
from numpy.random import rand, seed
import matplotlib.pyplot as plt

seed(123456)

# Brig Bashes, Melees, Whips
#   1 if the move used/hits in starting combo, 0 otherwise
#   If shield bash doesn't stun, whip might not hit
#   Melee accounted for automatically into simulation
combo_bash = 1
combo_whip = 1

# McCree Parameters
flash = False
fth = False
reload_time = 0.4
mc_accuracy = 0.99
mc_crit_percent = 0.99

mc_dmg = 70
mc_rate = 2
mc_health = 200 - combo_bash * 50 - combo_whip * 70
print('McCree Starting Health %d' % (mc_health,))
mc_armor = 0
mc_heal_rate = 0

if fth:
    mc_rate = 6.9
    mc_accuracy = 0.99
    mc_crit_percent = 0.0

brid_dmg = 35
brid_rate = 1/0.6
brid_health = 200
brid_armor = 50
brid_heal_rate = 16 # per second
if flash:
    brid_armor -= 25 - 5

rolled_once = False

time_res = 0.001
time = np.arange(0, 8, time_res)
mc_rng = rand(*time.shape)
mc_crit = rand(*time.shape)
# brid_rng = rand(*time.shape)

last_mc_shot = -9000
reload_time_start = -9000
last_brid_shot = -9000

mc_shot_count = 0

mccree = np.zeros((len(time), 2,))
bridge = np.zeros((len(time), 2,))

if combo_bash or combo_whip:
    flash_start = 1.0
    flash_end = 1.7
else:
    flash_start = 0.0
    flash_end = 0.7

for i in range(0, len(time)-1):
    current_time = time[i]
    if (current_time - last_mc_shot > (1.0 / mc_rate) and
        (current_time > 1.0 or (not combo_bash and not combo_whip))):
        # mccree shot attempt (rng accuracy)
        mc_shot_count += 1
        if mc_shot_count > 6:
            reload_time_start = current_time
            mc_shot_count = 0
            print('mccree begins reload at %.2f' % (current_time,))
        elif (mc_rng[i] < mc_accuracy and
            (current_time - reload_time_start) > reload_time and
            ((combo_bash or combo_whip) and current_time > 1.0)):
            print('%.2f: mccree hits (%d shots) %.2f, %.2f' % (current_time, mc_shot_count, mc_rng[i], mc_accuracy,))
            if mc_crit[i] >= mc_crit_percent:
                mc_dmg = 75
            else:
                print('mccree crits')
                mc_dmg = 75 * 2
            if brid_armor > 0:
                if mc_dmg > 10:
                    actual_dmg = int(mc_dmg - 5)
                else:
                    actual_dmg = int(mc_dmg / 2.0)
                brid_armor = brid_armor - actual_dmg
                if brid_armor < 0:
                    brid_health += brid_armor
                    brid_armor = 0
            else:
                actual_dmg = mc_dmg
                brid_health -= actual_dmg
        else:
            if (current_time - reload_time_start) > 1.5:
                print('%.2f: mccree misses (%d shots) %.2f, %.2f' % (current_time, mc_shot_count, mc_rng[i], mc_accuracy,))
            else:
                print('%.2f: mccree reloading' % current_time)

        if reload_time_start != current_time:
            last_mc_shot = current_time

        if reload_time_start >= 0 and current_time - reload_time_start > reload_time:
            if reload_time == 0.4: # already rolled once
                reload_time = 1.5
                rolled_once = True

    bridge[i:, 0] = brid_health
    bridge[i:, 1] = brid_armor
    if brid_health <= 0:
        print('brid died')
        break

    if current_time - last_brid_shot > (1.0 / brid_rate) and not (
        flash and flash_start < current_time < flash_end):
        # bridge mace hits (100% accuracy)
        print('%.2f: brig hits' % current_time)
        if mc_armor > 0:
            if brid_dmg > 10:
                actual_dmg = int(brid_dmg - 5)
            else:
                actual_dmg = int(brid_dmg / 2.0)
            mc_armor -= actual_dmg
            if mc_armor < 0:
                mc_health += mc_armor
                mc_armor = 0
        else:
            actual_dmg = brid_dmg
            mc_health -= actual_dmg

        last_brid_shot = current_time
    elif flash_start < current_time < flash_end:
        if (current_time * 200) % 10 == 0:
            print('%.2f: brig flashed'  % (current_time,))

    mccree[i:, 0] = mc_health
    mccree[i:, 1] = mc_armor
    if mc_health <= 0:
        print('mccree died')
        break

    # healing :)
    if mc_health < 200:
        mc_health += mc_heal_rate * time_res
    if brid_health + brid_armor < 250:
        brid_health += brid_heal_rate * time_res
        if brid_health > 200:
            diff = brid_health - 200
            brid_armor += diff
            brid_health = 200

mccree = np.clip(mccree, 0, None)
bridge = np.clip(bridge, 0, None)

plt.plot(time, mccree[:, 0] + mccree[:, 1], label='Total McCree')
plt.plot(time, bridge[:, 0] + bridge[:, 1], label='Total Brigitte')
plt.plot(time, bridge[:, 0], label='Brigitte Health Only')
if combo_bash and combo_whip:
    plt.title('Brigitte Full Combo, Flash %s, FTH %s, %.2f acc %.2f crit' % (
        flash, fth, mc_accuracy, mc_crit_percent,))
elif combo_bash:
    plt.title('Brigitte Bash Start, Flash %s, FTH %s, %.2f acc %.2f crit' % (
        flash, fth, mc_accuracy, mc_crit_percent,))
elif combo_whip:
    plt.title('Brigitte Whip Start, Flash %s, FTH %s, %.2f acc %.2f crit' % (
        flash, fth, mc_accuracy, mc_crit_percent,))
else:
    plt.title('Brigitte Melee Only, Flash %s, FTH %s, %.2f acc %.2f crit' % (
        flash, fth, mc_accuracy, mc_crit_percent,))

plt.legend()
plt.show()