from app.base import Character, EquipAt, Item, CanEquip, CanAttack
from app.status.afflictions import Burning, Freeze


class RustedSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "RustedSword",
                "description": "A worn-out and rusty sword with limited lifespan",
            },
            stat={"health": 5},
        )
        CanEquip.__init__(
            self,
            stat_to_equip={"strength": 13},
            equip_at=[EquipAt.HAND_LEFT, EquipAt.HAND_RIGHT],
        )
        CanAttack.__init__(self, stat_on_attack={"attack": 8})


class IronSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "IronSword",
                "description": "A sturdy and reliable iron sword",
            },
            stat={"health": 25},
        )
        CanEquip.__init__(
            self,
            stat_to_equip={"strength": 15},
            equip_at=[EquipAt.HAND_LEFT, EquipAt.HAND_RIGHT],
        )
        CanAttack.__init__(self, stat_on_attack={"attack": 12})


class SilverSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "SilverSword",
                "description": "A finely crafted silver sword with a gleaming blade",
            },
            stat={"health": 25},
        )
        CanEquip.__init__(
            self,
            stat_to_equip={"strength": 18},
            equip_at=[EquipAt.HAND_LEFT, EquipAt.HAND_RIGHT],
        )
        CanAttack.__init__(self, stat_on_attack={"attack": 18})


class FlameSword(Item, CanEquip, CanAttack):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FlameSword",
                "description": "A sword infused with the power of fire, emanating flames from its blade.",
            },
            stat={"health": 15},
        )
        CanEquip.__init__(
            self,
            stat_to_equip={"strength": 15, "intelligence": 10},
            equip_at=[EquipAt.HAND_LEFT, EquipAt.HAND_RIGHT],
        )
        CanAttack.__init__(self, stat_on_attack={"attack": 18})

    def can_crit(self, player: Character, opponent: Character | None) -> bool:
        if opponent is not None and "UNDEAD" in [
            opponent.flavor.category,
            opponent.flavor.sub_category,
        ]:
            return True
        return super().can_crit(player, opponent)

    def on_attack(self, player: Character, opponent: Character | None) -> int:
        if player._chance() > 75 and opponent is not None:
            opponent.apply(Burning())
        return super().on_attack(player, opponent)


class FrostSword(Item, CanEquip, CanAttack):
    # NOTE: Should implement a method to shoot ice bolts
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "FrostSword",
                "description": " A sword imbued with the chilling cold of ice, freezing enemies on impact.",
            },
        )
        CanEquip.__init__(
            self,
            stat_to_equip={"strength": 12, "intelligence": 8},
            equip_at=[EquipAt.HAND_LEFT, EquipAt.HAND_RIGHT],
        )
        CanAttack.__init__(self, stat_on_attack={"attack": 14})

    def on_attack(self, player: Character, opponent: Character | None) -> int:
        if player._chance() > 75 and opponent is not None:
            opponent.apply(Freeze())
        return super().on_attack(player, opponent)
