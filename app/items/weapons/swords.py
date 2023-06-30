from app.base import Item
from app.status.afflictions.elemental import Burning, Freeze


class RustedSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "RustedSword",
                "description": "A worn-out and rusty sword with limited lifespan",
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
                "description": "A sturdy and reliable iron sword",
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
                "description": "A finely crafted silver sword with a gleaming blade",
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
                "description": "A sword infused with the power of fire, emanating flames from its blade.",
                "category": "WEAPON",
                "sub_category": "MAGIC_SWORD",
            },
            stat={"health": 15, "attack": 18},
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


class FrostSword(Item):
    # NOTE: Should implement a method to shoot ice bolts
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FrostSword",
                "description": " A sword imbued with the chilling cold of ice, freezing enemies on impact.",
                "category": "WEAPON",
                "sub_category": "MAGIC_SWORD",
            },
            stat={"health": 15, "attack": 14},
            stat_to_equip={"strength": 12, "intelligence": 8},
            can_equip=True,
            can_attack=True,
            can_equip_at="HAND1",
        )
        self.freeze_probability = 25

    def on_attack(self):
        super().on_attack()
        if self.equipped_by.chance() < self.freeze_probability:
            self.equipped_by.opponent.apply(Freeze())
