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
        pass

    @property
    def can_start_battle_phase(self) -> bool:
        return True

    @property
    def can_end_battle_phase(self) -> bool:
        return True

    @property
    def can_start_turn_phase(self) -> bool:
        return True

    @property
    def can_end_turn_phase(self) -> bool:
        return True

    @property
    def can_start_player_attac_phase(self) -> bool:
        return True

    @property
    def can_start_end_attack_phase(self) -> bool:
        return True

    @property
    def can_start_opponent_attack_phase(self) -> bool:
        return True

    @property
    def can_end_opponent_attack_phase(self) -> bool:
        return True

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

    def on_start_end_attack_phase(self):
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


class CanHaveCustomAction:
    def __init__(self) -> None:
        self.actions: dict[str, Tuple[list[Phase], Callable]] = {}

    def get_available_actions(
        self, phase=Phase.BATTLE_NOT_STARTED, is_player=False
    ) -> dict[str, Callable]:
        if not is_player:
            if "OPPONENT_" in phase.value:
                phase = Phase[phase.value.replace("OPPONENT_", "PLAYER_")]
            else:
                phase = Phase[phase.value.replace("PLAYER_", "OPPONENT_")]

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
        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))

        self.can_equip: bool = kwargs.get("can_equip", False)
        self.can_unequip: bool = kwargs.get("can_unequip", False)
        self.can_consume: bool = kwargs.get("can_consume", False)
        self.can_attack: bool = kwargs.get("can_attack", False)
        self.can_defend: bool = kwargs.get("can_defend", False)

        self.stat_on_equip = Stat(**kwargs.get("stat_on_equip", {}))
        self.stat_to_equip = Stat(
            **kwargs.get("stat_to_equip", {"strength": float("inf")})
        )
        self.can_equip_at: str | None = kwargs.get("can_equip_at", None)

        self.stat_to_consume = Stat(**kwargs.get("stat_to_consume", {}))
        self.stat_on_consume = Stat(**kwargs.get("stat_on_consume", {}))

    def character_can_equip(self, equip_character: "Character") -> bool:
        return self.can_equip and equip_character.stat >= self.stat_to_equip

    def character_can_unequip(self, equip_character: "Character") -> bool:
        return (
            self.can_unequip
            and self.flavor.name in equip_character.equipped.group.keys()
        )

    def character_can_consume(self, consume_character: "Character") -> bool:
        return self.can_consume and consume_character.stat >= self.stat_to_consume

    def character_can_attack(self, equip_character: "Character") -> bool:
        return (
            self.can_attack
            and self.flavor.name in equip_character.equipped.group.keys()
        )

    def character_can_defend(self, equip_character: "Character") -> bool:
        return (
            self.can_defend
            and self.flavor.name in equip_character.equipped.group.keys()
        )

    def character_can_crit(self, equip_character: "Character") -> bool:
        return False

    def on_equip(self, equip_character: "Character"):
        if self.character_can_equip(equip_character):
            equip_character.stat += self.stat_on_equip

    def on_unequip(self, equip_character: "Character"):
        if self.character_can_unequip(equip_character):
            equip_character.stat -= self.stat_on_equip

    def on_consume(self, consume_character: "Character"):
        if self.character_can_consume(consume_character):
            consume_character.stat += self.stat_on_consume

    def get_attack(self, equip_character: "Character") -> int:
        if self.character_can_attack(equip_character) and self.stat.attack > 0:
            if self.character_can_crit(equip_character):
                return self.stat.attack * 2
            return self.stat.attack
        return 0

    def get_defend(self, equip_character: "Character") -> int:
        if self.character_can_defend(equip_character) and self.stat.defense > 0:
            return self.stat.defense
        return 0

    def on_attack(self, equip_character: "Character"):
        if equip_character.opponent is not None:
            actual_damage = (
                self.get_attack(equip_character)
                + equip_character.stat.attack
                - equip_character.opponent.defense_by_equipment
                - equip_character.opponent.stat.defense
            )

            equip_character.opponent.take_damage(actual_damage)


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


class Character(CanModifyPhase, CanHaveCustomAction):
    def __init__(self, **kwargs) -> None:
        CanModifyPhase.__init__(self)
        CanHaveCustomAction.__init__(self)
        self.is_player = False

        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))
        self.equipped = EquipGroup()

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
        for item in self.equipped.group.values():
            if item.character_can_defend(self):
                defense_by_equipment += item.get_defend(self)
        return defense_by_equipment

    @property
    def opponent(self) -> "Character | None":
        if self.is_player:
            return Context.opponent
        return Context.player

    def get_available_actions(self, phase=None, is_player=None) -> dict[str, Callable]:
        phase = Context.current_phase if phase is None else phase
        is_player = self.is_player if is_player is None else is_player

        return super().get_available_actions(phase, self.is_player)

    def can_equip(self, item: "Item") -> bool:
        return item.character_can_equip(self) and self.equipped.can_add(item)

    def can_unequip(self, item: "Item") -> bool:
        return item.character_can_unequip(self) and self.equipped.can_remove(item)

    def can_consume(self, item: "Item") -> bool:
        return item.character_can_consume(self)

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
            item.on_unequip(self)
            return self.equipped.remove(item)
        return None

    def perform_item_attack(self, **kwargs):
        if self.stat.agility > self.chance():
            for item in self.equipped.group.values():
                if item.character_can_attack(self):
                    item.on_attack(self)

    def heal(self, heal: int):
        if heal > 0:
            self.stat.health += heal

    def take_damage(self, damage: int):
        if damage > 0:
            self.stat.health -= damage


class Battle:
    def __init__(self, player: Character, opponent: Character) -> None:
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
