from enum import Enum
from attr import define, field, asdict
from typing import Any, Tuple, Callable
from random import randint


class Phase(Enum):
    BATTLE_NOT_STARTED = "BATTLE_NOT_STARTED"
    BATTLE_START = "BATTLE_START"
    BATTLE_END = "BATTLE_END"
    TURN_START = "TURN_START"
    TURN_END = "TURN_END"
    PLAYER_ATTACK_START = "PLAYER_ATTACK_START"
    PLAYER_ATTACK_END = "PLAYER_ATTACK_END"
    OPPONENT_ATTACK_START = "OPPONENT_ATTACK_START"
    OPPONENT_ATTACK_END = "OPPONENT_ATTACK_END"


class AttackStatus(Enum):
    ATTACK_POSSIBLE = "ATTACK_POSSIBLE"
    ATTACK_NOT_POSSIBLE = "ATTACK_NOT_POSSIBLE"
    ATTACK_MISSED = "ATTACK_MISSED"
    ATTACK_SUCCESS = "ATTACK_SUCCESS"


class DefendStatus(Enum):
    DEFEND_POSSIBLE = "DEFEND_POSSIBLE"
    DEFEND_NOT_POSSIBLE = "DEFEND_NOT_POSSIBLE"
    DEFEND_FAILED = "DEFEND_FAILED"
    DEFEND_SUCCESS = "DEFEND_SUCCESS"
    ATTACK_EVADED = "ATTACK_EVADED"


class CanModifyPhase:
    def __init__(self) -> None:
        self.functions_by_phase: dict[Phase, Callable] = {
            Phase.BATTLE_START: self.on_start_battle_phase,
            Phase.BATTLE_END: self.on_end_battle_phase,
            Phase.TURN_START: self.on_start_turn_phase,
            Phase.TURN_END: self.on_end_turn_phase,
            Phase.PLAYER_ATTACK_START: self.on_start_player_attack_phase,
            Phase.PLAYER_ATTACK_END: self.on_end_player_attack_phase,
            Phase.OPPONENT_ATTACK_START: self.on_start_opponent_attack_phase,
            Phase.OPPONENT_ATTACK_END: self.on_end_opponent_attack_phase,
        }

    def on_start_battle_phase(self):
        pass

    def on_end_battle_phase(self):
        pass

    def on_start_turn_phase(self):
        pass

    def on_end_turn_phase(self):
        pass

    def on_start_player_attack_phase(self):
        pass

    def on_end_player_attack_phase(self):
        pass

    def on_start_opponent_attack_phase(self):
        pass

    def on_end_opponent_attack_phase(self):
        pass

    def switch_to_phase(self, phase: Phase):
        if Context.current_phase == Phase.BATTLE_START and phase == Phase.TURN_START:
            Context.current_turn = 1
        if phase == Phase.TURN_END:
            Context.current_turn += 1
        Context.current_phase = phase
        self.run_phase_action()

    def run_phase_action(self):
        if Context.current_phase != Phase.BATTLE_NOT_STARTED:
            character_phase = Context.player.current_phase()
            Context.player.functions_by_phase[character_phase]()
            for item in Context.player.status_affect.group.values():
                item.functions_by_phase[character_phase]()
            for item in Context.player.equipped.group.values():
                item.functions_by_phase[character_phase]()

            character_phase = Context.opponent.current_phase()
            Context.opponent.functions_by_phase[character_phase]()
            for item in Context.opponent.status_affect.group.values():
                item.functions_by_phase[character_phase]()
            for item in Context.opponent.equipped.group.values():
                item.functions_by_phase[character_phase]()


class CanHaveCustomAction:
    def __init__(self) -> None:
        self.actions: dict[str, Tuple[list[Phase], Callable]] = {}

    def get_available_actions(
        self, phase=Phase.BATTLE_NOT_STARTED
    ) -> dict[str, Callable]:
        available_actions: dict[str, Callable] = {}
        for name, action in self.actions.items():
            if phase in action[0]:
                available_actions[name] = action[1]

        return available_actions

    def perform_action(self, action_name: str, **kwargs):
        if (value := self.actions.get(action_name, None)) is not None:
            value[1](**kwargs)

    def register_action(
        self, action_name: str, valid_action_phases: list[Phase], action: Callable
    ):
        self.actions[action_name] = (valid_action_phases, action)


@define
class FlavorStat:
    name: str = field(default="Unknown")
    description: str = field(default="")
    category: str = field(default="NO_CATEGORY")
    sub_category: str = field(default="")
    type: list[str] = field(default=[])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@define
class Stat:
    health: int = field(default=0)
    attack: int = field(default=0)
    defense: int = field(default=0)
    strength: int = field(default=0)
    intelligence: int = field(default=0)
    fatigue: int = field(default=0)
    mana: int = field(default=0)
    agility: int = field(default=0)
    luck: int = field(default=0)

    @property
    def is_alive(self):
        return self.health > 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __add__(self, stat: "Stat") -> "Stat":
        if isinstance(stat, Stat):
            self_dict, stat_dict = self.to_dict(), stat.to_dict()
            return Stat(**{k: self_dict[k] + stat_dict[k] for k in self_dict.keys()})

    def __sub__(self, stat: "Stat") -> "Stat":
        if isinstance(stat, Stat):
            self_dict, stat_dict = self.to_dict(), stat.to_dict()
            return Stat(**{k: self_dict[k] - stat_dict[k] for k in self_dict.keys()})

    def __ge__(self, stat: "Stat") -> bool:
        if isinstance(stat, Stat):
            self_dict, stat_dict = self.to_dict(), stat.to_dict()
            return all([self_dict[k] >= stat_dict[k] for k in self_dict.keys()])


class Item(CanModifyPhase, CanHaveCustomAction):
    def __init__(self, **kwargs) -> None:
        CanModifyPhase.__init__(self)
        CanHaveCustomAction.__init__(self)
        self.flavor: FlavorStat = FlavorStat(**kwargs.get("flavor", {}))
        self.stat: Stat = Stat(**kwargs.get("stat", {}))
        self.equipped_by: Character | None = None

        self.can_equip: bool = kwargs.get("can_equip", False)
        self.can_unequip: bool = kwargs.get("can_unequip", False)
        self.can_consume: bool = kwargs.get("can_consume", False)
        self.can_attack: bool = kwargs.get("can_attack", False)
        self.can_defend: bool = kwargs.get("can_defend", False)
        self.is_status_affect: bool = kwargs.get("is_status_affect", False)

        self.stat_on_equip = Stat(**kwargs.get("stat_on_equip", {}))
        self.stat_to_equip = Stat(
            **kwargs.get("stat_to_equip", {"strength": float("inf")})
        )
        self.can_equip_at: str | None = kwargs.get("can_equip_at", None)

        self.stat_to_consume = Stat(**kwargs.get("stat_to_consume", {}))
        self.stat_on_consume = Stat(**kwargs.get("stat_on_consume", {}))

    @property
    def is_active(self) -> bool:
        return self.stat.health > 0

    def character_can_equip(self, equip_character: "Character") -> bool:
        return self.can_equip and equip_character.stat >= self.stat_to_equip

    def character_can_unequip(self) -> bool:
        return (
            self.equipped_by is not None
            and self.can_unequip
            and self.flavor.name in self.equipped_by.equipped.group.keys()
        )

    def character_can_consume(self, consume_character: "Character") -> bool:
        return self.can_consume and consume_character.stat >= self.stat_to_consume

    def character_can_attack(self) -> bool:
        return (
            self.equipped_by is not None
            and self.can_attack
            and self.flavor.name in self.equipped_by.equipped.group.keys()
        )

    def character_can_defend(self) -> bool:
        return (
            self.equipped_by is not None
            and self.can_defend
            and self.flavor.name in self.equipped_by.equipped.group.keys()
        )

    def character_can_apply(self, affect_character: "Character") -> bool:
        return self.is_status_affect

    def character_can_unapply(self) -> bool:
        return (
            self.equipped_by is not None
            and self.is_status_affect
            and self.flavor.name in self.equipped_by.status_affect.group.keys()
        )

    def character_can_crit(self) -> bool:
        return False

    def on_equip(self, equip_character: "Character"):
        if self.character_can_equip(equip_character):
            self.equipped_by = equip_character
            self.equipped_by.stat += self.stat_on_equip

    def on_unequip(self):
        if self.equipped_by is not None and self.character_can_unequip():
            self.equipped_by.stat -= self.stat_on_equip
            self.equipped_by = None

    def on_apply(self, equip_character: "Character"):
        if self.character_can_apply(equip_character):
            self.equipped_by = equip_character

    def on_unapply(self):
        if self.equipped_by is not None and self.character_can_unequip():
            self.equipped_by = None

    def on_consume(self, consume_character: "Character"):
        if self.character_can_consume(consume_character):
            consume_character.stat += self.stat_on_consume

    def get_attack(self) -> int:
        if (
            self.equipped_by is not None
            and self.character_can_attack()
            and self.stat.attack > 0
        ):
            if self.character_can_crit():
                return self.stat.attack * 2
            return self.stat.attack
        return 0

    def get_defend(self) -> int:
        if (
            self.equipped_by is not None
            and self.character_can_defend()
            and self.stat.defense > 0
        ):
            return self.stat.defense
        return 0

    def on_attack(self):
        if self.equipped_by is not None and self.equipped_by.opponent is not None:
            actual_damage = (
                self.get_attack()
                + self.equipped_by.stat.attack
                - self.equipped_by.opponent.defense_by_equipment
                - self.equipped_by.opponent.stat.defense
            )
            self.equipped_by.opponent.take_damage(actual_damage)
            self.equipped_by.opponent.wear_out_defendables()
            self.wear_out()

    def wear_out(self):
        self.stat.health -= 1


class ItemGroup:
    def __init__(self, group: dict[str, Item], limit: int = 99) -> None:
        self.group = group
        self.limit = limit

    @property
    def is_full(self) -> bool:
        return len(self.group) >= self.limit

    def can_add(self, item: Item) -> bool:
        return item.flavor.name not in self.group and not self.is_full

    def can_remove(self, item: Item) -> bool:
        return item.flavor.name in self.group

    def add(self, item: Item) -> Item | None:
        if self.can_add(item):
            self.group[item.flavor.name] = item
            return item
        return None

    def remove(self, item: Item) -> Item | None:
        if self.can_remove(item):
            return self.group.pop(item.flavor.name)
        return None


class StatusGroup(ItemGroup):
    def __init__(self) -> None:
        super().__init__({})
        self.can_stack = False

    def can_add(self, item: Item) -> bool:
        if self.can_stack:
            return not self.is_full
        return super().can_add(item)

    def add(self, item: Item) -> Item | None:
        if self.can_add(item):
            if item.flavor.name in self.group.keys():
                self.group[item.flavor.name].stat += item.stat
                return self.group[item.flavor.name]
            super().add(item)
            return item
        return None

    def remove(self, item: Item) -> Item | None:
        if self.can_remove(item):
            return self.group.pop(item.flavor.name)
        return None


class EquipGroup(ItemGroup):
    def __init__(self) -> None:
        super().__init__({}, 11)

        self.equip_slots: dict[str, Item | None] = {
            "HEAD": None,
            "NECK": None,
            "TORSO": None,
            "HAND1": None,
            "HAND2": None,
            "FINGER1": None,
            "FINGER2": None,
            "WAIST": None,
            "LEG": None,
            "FOOT1": None,
            "FOOT2": None,
        }

    def can_add(self, item: Item) -> bool:
        return (
            super().can_add(item)
            and item.can_equip_at is not None
            and item.can_equip_at in self.equip_slots
            and self.equip_slots[item.can_equip_at] is None
        )

    def can_remove(self, item: Item) -> bool:
        return (
            super().can_remove(item)
            and item.can_equip_at is not None
            and item.can_equip_at in self.equip_slots
            and self.equip_slots[item.can_equip_at] == item
        )

    def add(self, item: Item) -> Item | None:
        if self.can_add(item) and item.can_equip_at is not None:
            super().add(item)
            self.equip_slots[item.can_equip_at] = item
            return item
        return None

    def remove(self, item: "Item") -> Item | None:
        if self.can_remove(item) and item.can_equip_at is not None:
            super().remove(item)
            self.equip_slots[item.can_equip_at] = None
            return item
        return None

    def equipped_at(self, item: "Item") -> str | None:
        for k, v in self.equip_slots.items():
            if v == item:
                return k
        return None

    def get_defendable_items(self) -> dict[str, Item]:
        return {
            k: self.group[k]
            for k in self.group.keys()
            if self.group[k].character_can_defend()
        }

    def get_attackable_items(self) -> dict[str, Item]:
        return {
            k: self.group[k]
            for k in self.group.keys()
            if self.group[k].character_can_attack()
        }


class Character(CanModifyPhase, CanHaveCustomAction):
    def __init__(self, **kwargs) -> None:
        CanModifyPhase.__init__(self)
        CanHaveCustomAction.__init__(self)
        self.is_player = False

        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))
        self.equipped = EquipGroup()
        self.status_affect = StatusGroup()

        self.__register_actions()

    def __register_actions(self):
        self.register_action(
            "perform_item_attack",
            [Phase.PLAYER_ATTACK_START],
            self.perform_item_attack,
        )

    def chance(self):
        return randint(1, 100 - self.stat.luck)

    @property
    def defense_by_equipment(self) -> int:
        defense_by_equipment = 0
        for item in self.equipped.get_defendable_items().values():
            defense_by_equipment += item.get_defend()
        return defense_by_equipment

    @property
    def opponent(self) -> "Character | None":
        if self.is_player:
            return Context.opponent
        return Context.player

    def current_phase(self) -> Phase:
        if not self.is_player:
            if "OPPONENT_" in Context.current_phase.value:
                return Phase[
                    Context.current_phase.value.replace("OPPONENT_", "PLAYER_")
                ]
            return Phase[Context.current_phase.value.replace("PLAYER_", "OPPONENT_")]
        return Context.current_phase

    def get_available_actions(self, phase=None) -> dict[str, Callable]:
        return super().get_available_actions(self.current_phase())

    def can_equip(self, item: "Item") -> bool:
        return item.character_can_equip(self) and self.equipped.can_add(item)

    def can_unequip(self, item: "Item") -> bool:
        return item.character_can_unequip() and self.equipped.can_remove(item)

    def can_consume(self, item: "Item") -> bool:
        return item.character_can_consume(self)

    def can_crit(self, item: "Item") -> bool:
        return item.character_can_crit()

    def can_apply(self, item: "Item") -> bool:
        return item.character_can_apply(self)

    def can_unapply(self, item: "Item") -> bool:
        return item.character_can_unapply()

    def consume(self, item: "Item") -> Item | None:
        if self.can_consume(item):
            item.on_consume(self)
            return item
        return None

    def equip(self, item: "Item") -> Item | None:
        if self.can_equip(item):
            item.on_equip(self)
            return self.equipped.add(item)
        return None

    def unequip(self, item: "Item") -> Item | None:
        if self.can_unequip(item):
            item.on_unequip()
            return self.equipped.remove(item)
        return None

    def apply(self, item: "Item") -> Item | None:
        if self.can_apply(item):
            item.on_apply(self)
            return self.status_affect.add(item)
        return None

    def unapply(self, item: "Item") -> Item | None:
        if self.can_unapply(item):
            item.on_unapply()
            return self.status_affect.remove(item)
        return None

    def wear_out_defendables(self):
        for item in self.equipped.get_defendable_items().values():
            item.wear_out()

    def perform_item_attack(self, **kwargs):
        if self.stat.agility > self.chance():
            for item in self.equipped.get_attackable_items().values():
                item.on_attack()

    def heal(self, heal: int):
        if heal > 0:
            self.stat.health += heal

    def take_damage(self, damage: int):
        if damage > 0:
            self.stat.health -= damage


class Battle(CanModifyPhase):
    def __init__(self, player: Character, opponent: Character) -> None:
        super().__init__()
        self.initiate(player, opponent)

    def initiate(self, player: Character, opponent: Character):
        Context.player = player
        Context.opponent = opponent

        Context.player.is_player = True
        Context.opponent.is_player = False


class Context:
    current_turn: int = 0
    player: "Character | None" = None
    opponent: "Character | None" = None
    current_phase: Phase = Phase.BATTLE_NOT_STARTED
