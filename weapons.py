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
    def __init__(
        self,
        owner,
        charge: ChargeAttack,
        base_damage=10,
        base_range=120,
        arc_deg=60,
        charge_threshold=0.3,
    ):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.base_range = base_range
        self.arc_deg = arc_deg
        self.charge_threshold = charge_threshold

    def attack(self, enemies, hold_time, direction):
        charge_factor = self.charge.factor(hold_time)
        damage = self.base_damage * (1 + charge_factor)
        attack_range = self.base_range * (1 + 0.5 * charge_factor)
        charged = hold_time >= self.charge_threshold
        hits = []
        if charged:
            arc = math.tau
            for enemy in enemies:
                dist = (enemy.pos - self.owner.pos).length()
                if dist <= attack_range:
                    enemy.take_damage(damage)
                    hits.append(enemy)
        else:
            arc = math.radians(self.arc_deg * (1 + 0.5 * charge_factor))
            for enemy in enemies:
                to_enemy = enemy.pos - self.owner.pos
                dist = to_enemy.length()
                if dist <= attack_range and dist > 0:
                    angle = math.acos(
                        max(-1.0, min(direction.dot(to_enemy.normalize()), 1.0))
                    )
                    if angle <= arc / 2:
                        enemy.take_damage(damage)
                        hits.append(enemy)
        return hits, attack_range, arc, charge_factor, charged


class RangedWeapon:
    def __init__(
        self,
        owner,
        charge: ChargeAttack,
        base_damage=5,
        projectile_speed=600,
        charge_threshold=0.3,
        burst_count=10,
        burst_interval=0.05,
        projectile_lifetime=2.0,
        charged_pierce=True,
    ):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.projectile_speed = projectile_speed
        self.charge_threshold = charge_threshold
        self.burst_count = burst_count
        self.burst_interval = burst_interval
        self.projectile_lifetime = projectile_lifetime
        self.charged_pierce = charged_pierce

    def attack(self, projectiles, hold_time, direction, on_hit=None):
        charge_factor = self.charge.factor(hold_time)
        damage = self.base_damage * (1 + charge_factor)
        speed = self.projectile_speed * (1 + charge_factor)
        velocity = direction * speed
        if hold_time >= self.charge_threshold:
            for i in range(self.burst_count):
                projectiles.append(
                    Projectile(
                        self.owner.pos,
                        velocity,
                        damage,
                        charge_factor=charge_factor,
                        on_hit=on_hit,
                        pierce=self.charged_pierce,
                        delay=i * self.burst_interval,
                        life_time=self.projectile_lifetime,
                    )
                )
        else:
            projectiles.append(
                Projectile(
                    self.owner.pos,
                    velocity,
                    damage,
                    charge_factor=charge_factor,
                    on_hit=on_hit,
                    life_time=self.projectile_lifetime,
                )
            )
