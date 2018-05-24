from copy import deepcopy
from overplay import Hero, Ability, run_simulation

flashbang = Ability(damage=25, healing=0.0, casttime=0.5, duration=0.7,
cooldown=10, has_stun=True, has_knockback=False, has_falloff=False, 
start_falloff=0.0, end_falloff=0.0, fallen_damage=0.0)

primary = Ability(damage=70, healing=0.0, casttime=0.0, duration = 0.0,
cooldown=1.0/2, has_falloff=True, start_falloff=22, end_falloff=45,
fallen_damage=22)

fth = Ability(damage=45*6, healing=0.0, casttime=0.0, duration=6 / 6.9, cooldown =
8, has_falloff=True, start_falloff=22, end_falloff=45, fallen_damage=22)

abilities = {
   'primary': primary,
   'fth': fth,
   'flashbang': flashbang,
}

McCree = Hero(health=200, armor=0, shields=0, ammo=6, **abilities)

