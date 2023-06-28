from app.base import Item, CanEquip, CanAttack, CanDefend


class RustedSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "RustedSword",
                "description": "A worn-out and rusty sword",
            },
        )
        CanEquip.__init__(self, stat_to_equip={"strength": 13})
        CanAttack.__init__(self, stat_on_attack={"attack": 8})


class IronSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "IronSword",
                "description": "A sturdy and reliable iron sword",
            },
        )
        CanEquip.__init__(self, stat_to_equip={"strength": 15})
        CanAttack.__init__(self, stat_on_attack={"attack": 12})


class SilverSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "SilverSword",
                "description": "A finely crafted silver sword with a gleaming blade",
            },
        )
        CanEquip.__init__(self, stat_to_equip={"strength": 18})
        CanAttack.__init__(self, stat_on_attack={"attack": 18})


class FlameSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FlameSword",
                "description": "A sword infused with the power of fire, emanating flames from its blade.",
            },
        )
        CanEquip.__init__(self, stat_to_equip={"strength": 15, "intelligence": 10})
        CanAttack.__init__(self, stat_on_attack={"attack": 18})

        # NOTE: Should implement a method to implement crit-damage on UNDEAD
        # NOTE: Should have a chance to inflict BURNING stat on enemy


class FrostSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FrostSword",
                "description": " A sword imbued with the chilling cold of ice, freezing enemies on impact.",
            },
        )
        CanEquip.__init__(self, stat_to_equip={"strength": 12, "intelligence": 8})
        CanAttack.__init__(self, stat_on_attack={"attack": 14})

        # NOTE: Should implement a method to shoot ice bolts
        # NOTE: Should have a chance to inflict FREEZE stat on enemy
