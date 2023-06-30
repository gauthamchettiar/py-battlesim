from app.base import Character, Item


class RustedSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "RustedSword",
                "description": "A worn-out and rusty sword with limited lifespan",
            },
            stat={"health": 5, "attack": 8},
            stat_to_equip={"strength": 5},
            can_equip=True,
            can_attack=True,
        )


class IronSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "IronSword",
                "description": "A sturdy and reliable iron sword",
            },
            stat={"health": 20, "attack": 12},
            stat_to_equip={"strength": 15},
            can_equip=True,
            can_attack=True,
        )


class SilverSword(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "SilverSword",
                "description": "A finely crafted silver sword with a gleaming blade",
            },
            stat={"health": 20, "attack": 18},
            stat_to_equip={"strength": 18},
            can_equip=True,
            can_attack=True,
        )


class FlameSword(Item):
    # NOTE: chance for BURNING
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FlameSword",
                "description": "A sword infused with the power of fire, emanating flames from its blade.",
            },
            stat={"health": 15, "attack": 18},
            stat_to_equip={"strength": 15, "intelligence": 10},
            can_equip=True,
            can_attack=True,
        )

    def character_can_crit(self, equip_character: Character) -> bool:
        if equip_character.opponent is not None and "UNDEAD" in [
            equip_character.opponent.flavor.category,
            equip_character.opponent.flavor.sub_category,
        ]:
            return True
        return False


class FrostSword(Item):
    # NOTE: chance for FREEZE
    # NOTE: Should implement a method to shoot ice bolts
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FrostSword",
                "description": " A sword imbued with the chilling cold of ice, freezing enemies on impact.",
            },
            stat={"health": 15, "attack": 14},
            stat_to_equip={"strength": 12, "intelligence": 8},
            can_equip=True,
            can_attack=True,
        )
