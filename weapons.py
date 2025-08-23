import math

from projectiles import Projectile


class ChargeAttack:
    """Binary charge logic with progress helper."""

    def __init__(self, threshold: float):
        self.threshold = threshold

    def progress(self, hold_time: float) -> float:
        if self.threshold <= 0:
            return 1.0
        return max(0.0, min(hold_time / self.threshold, 1.0))

    def charged(self, hold_time: float) -> bool:
        return hold_time >= self.threshold


class MeleeWeapon:
    def __init__(self, owner, charge: ChargeAttack, base_damage=10, base_range=120, arc_deg=120):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.base_range = base_range
        self.arc_deg = arc_deg

    def attack(self, enemies, hold_time, direction):
        charged = self.charge.charged(hold_time)
        damage = self.base_damage
        attack_range = self.base_range
        hits = []
        if charged:
            arc = math.tau
            for enemy in enemies:
                dist = (enemy.pos - self.owner.pos).length()
                if dist <= attack_range:
                    enemy.take_damage(damage)
                    hits.append(enemy)
        else:
            arc = math.radians(self.arc_deg)
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
        return hits, attack_range, arc, charged


class RangedWeapon:
    def __init__(
        self,
        owner,
        charge: ChargeAttack,
        base_damage=5,
        projectile_speed=600,
        burst_count=10,
        burst_interval=0.05,
        projectile_lifetime=2.0,
        charged_pierce=True,
    ):
        self.owner = owner
        self.charge = charge
        self.base_damage = base_damage
        self.projectile_speed = projectile_speed
        self.burst_count = burst_count
        self.burst_interval = burst_interval
        self.projectile_lifetime = projectile_lifetime
        self.charged_pierce = charged_pierce
        self.burst_timer = 0.0

    def update(self, dt):
        if self.burst_timer > 0:
            self.burst_timer = max(0.0, self.burst_timer - dt)

    def attack(self, projectiles, hold_time, direction):
        if self.burst_timer > 0:
            return
        velocity = direction * self.projectile_speed
        damage = self.base_damage
        charged = self.charge.charged(hold_time)
        if charged:
            self.burst_timer = self.burst_interval * self.burst_count
            for i in range(self.burst_count):
                projectiles.append(
                    Projectile(
                        self.owner.pos,
                        velocity,
                        damage,
                        charge_factor=1.0,
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
                    charge_factor=0.0,
                    life_time=self.projectile_lifetime,
                )
            )
