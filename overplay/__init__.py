import numpy as np
from matplotlib import pyplot as plt

class Ability(object):
    def __init__(self, damage=0.0, healing=0.0, ammo_used=0.0,
    casttime=0.0, duration=0.0, cooldown=0.0,
    has_stun=False, has_knockback=False,
    has_falloff=False, start_falloff=0.0, end_falloff=0.0, fallen_damage=0.0):
        self.damage = damage
        self.healing = healing
        self.casttime = casttime
        self.duration = duration
        if self.duration < 0.001: # 1 "tick"
            self.duration = 0.001
        self.cooldown = cooldown

        self.activation_delay = self.casttime + self.duration + self.cooldown

        self.has_stun = has_stun
        self.has_knockback = has_knockback
        self.has_falloff = has_falloff
        self.start_falloff = start_falloff
        self.end_falloff = end_falloff
        self.fallen_damage = fallen_damage

        self.last_activation = -9000

    def activate(self, current_time, accuracy, range_):
        if current_time - self.last_activation < self.activation_delay:
            '''
            Ability still on cooldown
            '''
            return (False,)

        '''
        Attempt to use ability
        '''
        self.last_activation = current_time

        hps = self.healing / self.duration

        effective_damage = self.damage
        if self.has_falloff and range_ > self.start_falloff:
            if range_ > self.end_falloff:
                effective_damage = fallen_damage
            else:
                percent_fallen = 1 - ((self.end_falloff - range_) /
                (self.end_falloff - self.start_falloff))
                effective_damage = ((1 - percent_fallen) * self.damage +
                    (percent_fallen) * self.fallen_damage)
            
        dps = effective_damage / self.duration
        
        if np.random.random() > accuracy:
            '''
            Ability missed
            '''
            return (True, dps, hps, self.has_stun, 0, 0)

        '''
        Ability hit
        '''
        return (True, dps, hps, self.has_stun, self.casttime, self.duration)

class Hero(object):
    '''
    TODO(buckbaskin): add casting time, duration split
    TODO(buckbaskin): add ammo usage
    '''
    def __init__(self, health, armor, shields, ammo, shield_delay = 1.0,
        shield_regen = 30, **abilities):
        self.abilities = abilities
        self.active_abilities = {}
        self.base_health = health
        self.health = health
        self.base_armor = armor
        self.armor = armor
        self.base_shields = shields
        self.shields = shields
        self.shield_delay = shield_delay
        self.shield_regen = shield_regen
        self.last_damage = -9000
        self.base_ammo = ammo
        self.ammo = ammo

        self.is_casting_until = -9000

    def _update_abilities(self, current_time, new_abilities, time_step=0.001):
        for ability_name, accuracy, range_ in new_abilities:
            result = self.abilities[ability_name].activate(current_time,
            accuracy, range_)
            if not result[0]:
                continue
            activated, dps, hps, has_stun, casttime, duration = result
            if duration <= 0.0:
                continue
            self.active_abilities[ability_name] = {
                'start_time': current_time + casttime,
                'end_time': current_time + casttime + duration,
                'dps': dps,
                'hps': hps,
                'has_stun': has_stun,
            }
        damage_out = 0.0
        healing_in = 0.0
        for ability_name in self.active_abilities:
            ability_state = self.active_abilities[ability_name]
            if ability_state['start_time'] <= current_time < ability_state['end_time']:
                damage_out += ability_state['dps'] * time_step
                healing_in += ability_state['hps'] * time_step

        return (damage_out, healing_in,)
        
    def _update_healthbar(self, current_time, damage, healing):
        '''
        Update the quantities for a single simulation tick
        '''
        net_damage = damage
        if net_damage > 0.0:
            self.last_damage = current_time
        if self.armor > 0:
            if net_damage <= 10:
                net_damage = net_damage * 0.5
            else:
                net_damage -= 5

        if self.shields > 0:
            if net_damage <= self.shields:
                self.shields -= net_damage
                net_damage = 0.0
            else:
                net_damage -= self.shields
                self.shields = 0.0

        if self.armor > 0:
            if net_damage <= self.armor:
                self.armor -= net_damage
                net_damage = 0.0
            else:
                net_damage -= self.armor
                self.armor = 0.0

        if self.health > 0:
            if net_damage <= self.health:
                self.health -= net_damage
                net_damage = 0.0
            else:
                self.health = 0.0
                net_damage = 0.0

        if self.health > 0:
            '''
            Not dead yet
            '''
            self.health += healing
            if self.health > self.base_health:
                healing = self.health - self.base_health
                self.health = self.base_health
            else:
                healing = 0.0
            
            self.armor += healing
            if self.armor > self.base_armor:
                healing = self.armor - self.base_armor
                self.armor = self.base_armor
            else:
                healing = 0.0

            self.shields += healing
            if self.shields > self.base_shields:
                healing = self.shields - self.base_shields
                self.shields = self.base_shields
            else:
                healing = 0.0

            if current_time - self.last_damage > self.shield_delay:
                self.shields += self.shield_regen
                if self.shields > self.base_shields:
                    self.shields = self.base_shields

        if self.health < 0.0:
            self.health = 0.0

        return (self.health, self.armor, self.shields)

def run_simulation(hero1, hero2, schedule1 = {}, schedule2 = {}):
    '''
    schedule is a dictionary where the key is the time in milliseconds and the value
    is a list of abilities to try and use (often just 1)
    '''
    np.random.seed(12345)
    time_step = 0.001
    times = np.arange(0, 10, time_step)
    healthbar1 = np.zeros((times.shape[0], 3))
    healthbar2 = np.zeros((times.shape[0], 3))
    for index, current_time in enumerate(times):
        activations = []
        if index in schedule1:
            activations = schedule1[index]
        h1d, h1h = hero1._update_abilities(current_time, activations, time_step)
        activations = []
        if index in schedule2:
            activations = schedule2[index]
        h2d, h2h = hero2._update_abilities(current_time, activations, time_step)

        h1health, h1armor, h1shields = hero1._update_healthbar(current_time, h2d, h1h)
        h2health, h2armor, h2shields = hero2._update_healthbar(current_time, h1d, h2h)

        if h1health <= 0.0 or h2health <= 0.0:
            healthbar1[index:, 0] = h1health
            healthbar1[index:, 1] = h1armor
            healthbar1[index:, 2] = h1shields
            healthbar2[index:, 0] = h2health
            healthbar2[index:, 1] = h2armor
            healthbar2[index:, 2] = h2shields
            break
            

        healthbar1[index, 0] = h1health
        healthbar1[index, 1] = h1armor
        healthbar1[index, 2] = h1shields
        healthbar2[index, 0] = h2health
        healthbar2[index, 1] = h2armor
        healthbar2[index, 2] = h2shields

    healthbar1 = np.sum(healthbar1, axis=1)
    healthbar2 = np.sum(healthbar2, axis=1)

    plt.plot(times, healthbar1, label='hero1')
    plt.plot(times, healthbar2, label='hero2')
    plt.legend()
    plt.tight_layout()
    plt.show()

