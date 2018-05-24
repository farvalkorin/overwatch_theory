import numpy as np


class Ability(object):
    def __init__(self, damage=0.0, healing=0.0, runtime=0.0, cooldown=0.0, has_stun=False,
    has_knockback=False, has_falloff=False, start_falloff=0.0, end_falloff=0.0,
    fallen_damage=0.0):
        self.damage = damage
        self.healing = healing
        self.runtime = runtime
        if self.runtime < 0.001: # 1 "tick"
            self.runtime = 0.001
        self.cooldown = cooldown

        self.activation_delay = self.runtime + self.cooldown

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
        Use ability
        '''
        hps = self.healing / self.runtime

        effective_damage = self.damage
        if has_falloff and range_ > self.start_falloff:
            if range_ > self.end_falloff:
                effective_damage = fallen_damage
            else:
                percent_fallen = 1 - ((self.end_falloff - range_) /
                (self.end_falloff - self.start_falloff))
                effective_damage = (1 - percent_fallen) * self.damage +
                (percent_fallen) * self.fallen_damage
            
        dps = effective_damage / self.runtime
        
        if np.random.random() > accuracy:
            '''
            Ability missed
            '''
            return (True, dps, hps, self.has_stun, 0)

        '''
        Ability hit
        '''
        return (True, dps, hps, self.has_stun, self.runtime)



class Hero(object):
    def __init__(self, health, armor, shields, shield_delay = 1.0,
        shield_regen = 30, **abilities):
        self.abilities = abilities
        self.base_health = health
        self.health = health
        self.base_armor = armor
        self.armor = armor
        self.base_shields = shields
        self.shields = shields
        self.shield_delay = shield_delay
        self.shield_regen = shield_regen
        self.last_damage = -9000
    
    def update(self, current_time, damage, healing):
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

