from app.base import Item, Phase
from app.status.afflictions.elemental import Burning, Freeze
from textwrap import dedent


class RustedSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "RustedSword",
                "description": dedent(
                    """
                    A worn-out and rusty sword with limited lifespan.
                    - [HEAVY] Increases Fatigue
                    """
                ),
                "category": "WEAPON",
                "sub_category": "SWORD",
            },
            stat={"health": 5, "attack": 8},
            stat_to_equip={"strength": 5},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )


class IronSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "IronSword",
                "description": dedent(
                    """
                    A sturdy and reliable iron sword
                    - [ATTACK] Has Good Health
                    - [HEAVY] Increases Fatigue
                    """
                ),
                "category": "WEAPON",
                "sub_category": "SWORD",
            },
            stat={"health": 20, "attack": 12},
            stat_to_equip={"strength": 15},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )


class SilverSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "SilverSword",
                "description": dedent(
                    """
                    A finely crafted silver sword with a gleaming blade.
                    - [ATTACK] Has Good Health
                    """
                ),
                "category": "WEAPON",
                "sub_category": "SWORD",
            },
            stat={"health": 20, "attack": 18},
            stat_to_equip={"strength": 18},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )


class FlameSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FlameSword",
                "description": dedent(
                    """
                    A sword infused with the power of fire, emanating flames from its blade. 
                    - [CRIT] Higher damage on UNDEAD
                    - [ATTACK] Has Chance to inflict BURNING
                    - [MAGIC INFUSED] will wear out faster.]
                    """
                ),
                "category": "WEAPON",
                "sub_category": "MAGIC_SWORD",
            },
            stat={"health": 14, "attack": 5},
            stat_to_equip={"strength": 15, "intelligence": 10},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )
        self.burning_probability = 25

    def character_can_crit(self) -> bool:
        if (
            self.equipped_by is not None
            and self.equipped_by.opponent is not None
            and "UNDEAD"
            in [
                self.equipped_by.opponent.flavor.category,
                self.equipped_by.opponent.flavor.sub_category,
            ]
        ):
            return True
        return False

    def on_attack(self):
        super().on_attack()
        if self.equipped_by.chance() < self.burning_probability:
            self.equipped_by.opponent.apply(Burning())

    def wear_out(self):
        self.stat.health -= 2


class FrostSword(Item):
    # NOTE: Should implement a method to shoot ice bolts
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FrostSword",
                "description": dedent(
                    """
                    A sword imbued with the chilling cold of ice, freezing enemies on impact. 
                    - [ATTACK] Has Chance to inflict FREEZE
                    - [-4 MANA] Can shoot ICE BOLTS, has higher chance of inflicting FREEZE
                    - [MAGIC INFUSED] Will wear out faster.]
                    """
                ),
                "category": "WEAPON",
                "sub_category": "MAGIC_SWORD",
            },
            stat={"health": 14, "attack": 5},
            stat_to_equip={"strength": 12, "intelligence": 8},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )
        self.freeze_probability = 25
        self.ice_bolt_freeze_probability = 60
        self.__register_actions()

    def __register_actions(self):
        self.register_action(
            "shoot_ice_bolts", [Phase.PLAYER_ATTACK_START], self.shoot_ice_bolts
        )

    def on_attack(self):
        super().on_attack()
        if (
            self.equipped_by is not None
            and self.equipped_by.opponent is not None
            and self.equipped_by.chance() < self.freeze_probability
        ):
            self.equipped_by.opponent.apply(Freeze())

    def shoot_ice_bolts(self, **kwargs):
        if (
            self.equipped_by is not None
            and self.equipped_by.opponent is not None
            and self.equipped_by.stat.mana >= 4
        ):
            if self.equipped_by.chance() < self.ice_bolt_freeze_probability:
                self.equipped_by.opponent.apply(Freeze())
            self.equipped_by.opponent.take_damage(
                15
                - self.equipped_by.opponent.defense_by_equipment
                - self.equipped_by.opponent.stat.defense
            )
            self.wear_out()

    def wear_out(self):
        self.stat.health -= 2
