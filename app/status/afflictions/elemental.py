from app.base import Character, Item


class Burning(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Burning",
                "description": "On affliction loose 5 health and for next 2 turns, Every turn loose 1 defense and 2 health.",
                "category": "AFFLICTION",
            },
            stat={"health": 2},
            is_status_affect=True,
        )

    def on_apply(self, equip_character: Character):
        super().on_apply(equip_character)
        equip_character.stat.health -= 5

    def on_start_turn_phase(self):
        if self.is_active and self.equipped_by is not None:
            self.equipped_by.stat.defense -= 1
            self.equipped_by.stat.health -= 2
            self.stat.health -= 1


class Freeze(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Freeze",
                "description": "For next 3 turns, Your agility will be 0.",
                "category": "AFFLICTION",
            },
            stat={"health": 2},
            is_status_affect=True,
        )
        self.original_agility = 0

    def on_apply(self, equip_character: Character):
        super().on_apply(equip_character)
        self.original_agility = equip_character.stat.agility
        equip_character.stat.agility = 0

    def on_start_turn_phase(self):
        if not self.is_active:
            if self.equipped_by is not None:
                self.equipped_by.stat.agility = self.original_agility
        else:
            self.stat.health -= 1
