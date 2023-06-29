from app.base import Character, Item, IsStatus


class Poisoned(Item, IsStatus):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Poisoned",
                "description": "Unless removed, Every time you attack loose 1 Health.",
                "category": "AFFLICTION",
            },
        )
        IsStatus.__init__(self)

    def on(self, player: Character, opponent: Character | None, stage: str, **kwargs):
        if self.is_active and stage == "character_post_attack":
            player.stat.health -= 1


class Burning(Item, IsStatus):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Burning",
                "description": "For 3 turns, Every time you attack loose 1 defense and 2 health.",
                "category": "AFFLICTION",
            },
        )
        IsStatus.__init__(self)
        self.counter = 3

    def on(self, player: Character, opponent: Character | None, stage: str, **kwargs):
        if self.is_active and stage == "character_post_attack":
            if self.counter > 0:
                player.stat.health -= 2
                player.stat.defense -= 1
                self.counter -= 1
        if self.counter == 0:
            self.is_active = False


class Freeze(Item, IsStatus):
    def __init__(self) -> None:
        Item.__init__(
            self,
            flavor={
                "name": "Freeze",
                "description": "For next 3 turns, Your agility will be 0.",
                "category": "AFFLICTION",
            },
        )
        IsStatus.__init__(self)
        self.counter = 3
        self.original_agility = 0

    def on_apply(self, player: Character, opponent: Character | None):
        self.original_agility = player.stat.agility
        player.stat.agility = 0

    def on(self, player: Character, opponent: Character | None, stage: str, **kwargs):
        if self.is_active and stage in [
            "character_post_attack",
            "character_post_defend",
        ]:
            if self.counter > 0:
                self.counter -= 1
        if self.counter == 0:
            player.stat.agility = self.original_agility
            self.is_active = False
