import math
import pygame

from projectiles import Projectile


class ChargeAttack:
    """Compute charge factor based on hold time."""
    def __init__(self, max_charge_time: float):
        self.max_charge_time = max_charge_time

    def factor(self, hold_time: float) -> float:
        if self.max_charge_time <= 0:
            return 1.0
        return max(0.0, min(hold_time / self.max_charge_time, 1.0))


class MeleeWeapon:
    def __init__(self, owner, charge: ChargeAttack, base_damage=10, base_range=60, arc_deg=60):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.base_range = base_range
        self.arc_deg = arc_deg

    def attack(self, enemies, hold_time, direction):
        charge_factor = self.charge.factor(hold_time)
        damage = self.base_damage * (1 + charge_factor)
        attack_range = self.base_range * (1 + 0.5 * charge_factor)
        arc = math.radians(self.arc_deg * (1 + 0.5 * charge_factor))
        hits = []
        for enemy in enemies:
            to_enemy = enemy.pos - self.owner.pos
            dist = to_enemy.length()
            if dist <= attack_range and dist > 0:
                angle = math.acos(max(-1.0, min(direction.dot(to_enemy.normalize()), 1.0)))
                if angle <= arc / 2:
                    enemy.take_damage(damage)
                    hits.append(enemy)
        return hits


class RangedWeapon:
    def __init__(self, owner, charge: ChargeAttack, base_damage=5, projectile_speed=600):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.projectile_speed = projectile_speed

    def attack(self, projectiles, hold_time, direction):
        charge_factor = self.charge.factor(hold_time)
        damage = self.base_damage * (1 + charge_factor)
        speed = self.projectile_speed * (1 + charge_factor)
        velocity = direction * speed
        projectiles.append(Projectile(self.owner.pos, velocity, damage))
