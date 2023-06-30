from app.base import Character, Item


class Poisoned(Item):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Poisoned",
                "description": "Unless removed, Loose 1 Health Every Turn.",
                "category": "AFFLICTION",
            },
            stat={"health": 1},
            is_status_affect=True,
        )

    def on_start_turn_phase(self):
        if self.is_active and self.equipped_by is not None:
            self.equipped_by.stat.health -= 1
