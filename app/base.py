from enum import Enum
import random
from attrs import define, field
from attrs import asdict

from typing import Any, cast

# TODO : Add logic for StatusEffect/Ability
# TODO : Add logic for weapons to have custom actions


class AttackStatus(Enum):
    ATTACK_MISSED = "ATTACK_MISSED"
    ATTACK_SUCCESS = "ATTACK_SUCCESS"
    ATTACK_NOT_POSSIBLE = "ATTACK_NOT_POSSIBLE"


class DefendStatus(Enum):
    DEFEND_FAILED = "DEFEND_FAILED"
    DEFEND_SUCCESS = "DEFEND_SUCCESS"
    DEFEND_NOT_POSSIBLE = "DEFEND_NOT_POSSIBLE"
    ATTACK_EVADED = "ATTACK_EVADED"


class EquipAt(Enum):
    HAND_LEFT = "HAND_LEFT"
    HAND_RIGHT = "HAND_RIGHT"
    FEET_LEFT = "FEET_LEFT"
    FEET_RIGHT = "FEET_RIGHT"
    FINGER1 = "FINGER1"
    FINGER2 = "FINGER2"
    WAIST = "WAIST"
    NECK = "NECK"
    HEAD = "HEAD"


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


class Item:
    def __init__(self, **kwargs) -> None:
        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))


class ItemGroup:
    def __init__(self, group: dict[str, Any]) -> None:
        self.group = group

    def add(self, item: Any) -> Any | None:
        if item.flavor.name not in self.group:
            self.group[item.flavor.name] = item
            return item
        return None

    def remove(self, item: Any) -> Any | None:
        if item.flavor.name in self.group:
            return self.group.pop(item.flavor.name)
        return None

    def _get_filtered(self, cls_filter) -> dict[str, Any]:
        return {
            k: self.group[k]
            for k in self.group.keys()
            if isinstance(self.group[k], cls_filter)
        }

    def get_items_that_can_attack(self) -> dict[str, "CanAttack"]:
        return self._get_filtered(CanAttack)

    def get_items_that_can_defend(self) -> dict[str, "CanDefend"]:
        return self._get_filtered(CanDefend)


class EquipGroup(ItemGroup):
    def __init__(self) -> None:
        super().__init__(cast(dict[str, "Item | CanEquip"], {}))
        self.equip_slots: dict[EquipAt, Item | None] = {k: None for k in EquipAt}

    def add(self, item: "Item | CanEquip") -> Item | None:
        if (_can_equip_at := self.can_equip_at(item)) is not None and (
            equipped_item := super().add(item)
        ) is not None:
            self.equip_slots[_can_equip_at] = equipped_item
            return equipped_item
        return None

    def remove(self, item: "Item | CanEquip") -> Item | None:
        if (_equipped_at := self.equipped_at(item)) is not None and (
            unequipped_item := super().remove(item)
        ) is not None:
            self.equip_slots[_equipped_at] = None
            return unequipped_item
        return None

    def equipped_at(self, item: "Item | CanEquip") -> EquipAt | None:
        for k, v in self.equip_slots.items():
            if v == item:
                return k
        return None

    def can_equip_at(self, item: "Item | CanEquip") -> EquipAt | None:
        if isinstance(item, CanEquip):
            for equip_at in item.equip_at:
                if self.equip_slots[equip_at] is None:
                    return equip_at
        return None


class StatusGroup(ItemGroup):
    def __init__(self) -> None:
        super().__init__(cast(dict[str, "Item | IsStatus"], {}))


class CanEquip:
    def __init__(self, **kwargs) -> None:
        self.stat_to_equip = Stat(**kwargs.get("stat_to_equip", {}))
        self.stat_on_equip = Stat(**kwargs.get("stat_on_equip", {}))
        self.equip_at: list[EquipAt] = kwargs.get("equip_at", [])

    def can_equip(self, player: "Character", opponent: "Character | None") -> bool:
        return player.stat >= self.stat_to_equip and len(self.equip_at) > 0

    def can_unequip(self, player: "Character", opponent: "Character | None") -> bool:
        return True

    def on_equip(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_on_equip", item=self)
        player.stat += self.stat_on_equip

    def on_unequip(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_on_unequip", item=self)
        player.stat -= self.stat_on_equip


class CanConsume:
    def __init__(self, **kwargs) -> None:
        self.stat_to_consume = Stat(**kwargs.get("stat_to_consume", {}))
        self.stat_on_consume = Stat(**kwargs.get("stat_on_consume", {}))

    def can_consume(self, player: "Character", opponent: "Character | None") -> bool:
        return player.stat >= self.stat_to_consume

    def on_consume(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_on_consume", item=self)
        player.stat += self.stat_on_consume


class CanAttack:
    def __init__(self, **kwargs) -> None:
        self.stat_on_attack = Stat(**kwargs.get("stat_on_attack", {}))

    def can_attack(self, player: "Character", opponent: "Character | None") -> bool:
        return True

    def can_crit(self, player: "Character", opponent: "Character | None") -> bool:
        return False

    def pre_attack(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_pre_attack", item=self)
        player.stat += self.stat_on_attack
        player.stat.attack += (
            self.stat_on_attack.attack if self.can_crit(player, opponent) else 0
        )

    def post_attack(
        self, player: "Character", opponent: "Character | None", damage_done=None
    ):
        player.invoke_status_effect("item_post_attack", item=self)
        player.stat -= self.stat_on_attack
        player.stat.attack -= (
            self.stat_on_attack.attack if self.can_crit(player, opponent) else 0
        )

    def on_attack(self, player: "Character", opponent: "Character | None") -> int:
        self.pre_attack(player, opponent)
        damage_done = opponent.defend() if opponent is not None else 0
        self.post_attack(player, opponent, damage_done=damage_done)
        return damage_done


class CanDefend:
    def __init__(self, **kwargs) -> None:
        self.stat_on_defend = Stat(**kwargs.get("stat_on_defend", {}))

    def can_defend(self, player: "Character", opponent: "Character | None"):
        return True

    def pre_defend(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_pre_defend", item=self)
        player.stat += self.stat_on_defend

    def post_defend(
        self, player: "Character", opponent: "Character | None", damage_done=None
    ):
        player.invoke_status_effect("item_post_defend", item=self)
        player.stat -= self.stat_on_defend


class IsStatus:
    def __init__(self, **kwargs) -> None:
        self.is_active = True

    def can_apply(self, player: "Character", opponent: "Character | None") -> bool:
        return True

    def can_unapply(self, player: "Character", opponent: "Character | None") -> bool:
        return True

    def on_apply(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_on_apply", item=self)

    def on_unapply(self, player: "Character", opponent: "Character | None"):
        player.invoke_status_effect("item_on_unapply", item=self)

    def on(
        self, player: "Character", opponent: "Character | None", stage: str, **kwargs
    ):
        pass


class Character:
    def __init__(self, **kwargs) -> None:
        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))

        self.equipped = EquipGroup()
        self.status_effect = StatusGroup()

        self.opponent: Character | None = None

    def calculated_attack(self) -> int:
        if self.can_crit():
            return self.stat.attack * 2
        return self.stat.attack

    def can_attack(self) -> bool:
        return self.stat.agility >= self._chance()

    def can_crit(self) -> bool:
        return False

    def can_evade(self) -> bool:
        return self.stat.agility >= self._chance()

    def can_defend(self) -> bool:
        return True

    def can_equip(self, item: "Item") -> bool:
        return (
            isinstance(item, Item)
            and isinstance(item, CanEquip)
            and item.can_equip(player=self, opponent=self.opponent)
        )

    def can_unequip(self, item: "Item") -> bool:
        return (
            isinstance(item, Item)
            and isinstance(item, CanEquip)
            and item.can_unequip(player=self, opponent=self.opponent)
        )

    def can_consume(self, item: "Item") -> bool:
        return (
            isinstance(item, Item)
            and isinstance(item, CanConsume)
            and item.can_consume(player=self, opponent=self.opponent)
        )

    def can_apply(self, item: "Item") -> bool:
        return (
            isinstance(item, Item)
            and isinstance(item, IsStatus)
            and item.can_apply(player=self, opponent=self.opponent)
        )

    def can_unapply(self, item: "Item") -> bool:
        return (
            isinstance(item, Item)
            and isinstance(item, IsStatus)
            and item.can_unapply(player=self, opponent=self.opponent)
        )

    def initiate_battle(self, opponent: "Character"):
        self.opponent = opponent

    def attack(self) -> int:
        attack_status = self._attack_status()
        self.invoke_status_effect("character_pre_attack", attack_status=attack_status)
        if attack_status is AttackStatus.ATTACK_SUCCESS:
            damage_done = 0
            for item in self.equipped.get_items_that_can_attack().values():
                if item.can_attack(player=self, opponent=self.opponent):
                    damage_done += item.on_attack(player=self, opponent=self.opponent)
            self.invoke_status_effect(
                "character_post_attack",
                attack_status=attack_status,
                damage_done=damage_done,
            )
            return damage_done
        self.invoke_status_effect(
            "character_post_attack", attack_status=attack_status, damage_done=0
        )
        return 0

    def defend(self) -> int:
        defend_status = self._defend_status()
        opponent_attack = (
            self.opponent.calculated_attack()
            if isinstance(self.opponent, Character)
            else 0
        )
        self.invoke_status_effect(
            "character_pre_defend",
            attack_status=defend_status,
            opponent_attack=opponent_attack,
        )
        if defend_status is DefendStatus.DEFEND_SUCCESS:
            defendable_items = [
                item
                for item in self.equipped.get_items_that_can_defend().values()
                if item.can_defend(player=self, opponent=self.opponent)
            ]

            for item in defendable_items:
                item.pre_defend(player=self, opponent=self.opponent)

            opponent_attack -= self.stat.defense if len(defendable_items) > 0 else 0

            self._take_damage(opponent_attack)

            for item in defendable_items:
                item.post_defend(player=self, opponent=self.opponent)
            self.invoke_status_effect(
                "character_post_defend",
                attack_status=defend_status,
                opponent_attack=opponent_attack,
            )
            return opponent_attack
        elif defend_status in [
            DefendStatus.DEFEND_NOT_POSSIBLE,
            DefendStatus.DEFEND_FAILED,
        ]:
            self._take_damage(opponent_attack)
            self.invoke_status_effect(
                "character_post_defend",
                attack_status=defend_status,
                opponent_attack=opponent_attack,
            )
            return opponent_attack
        self.invoke_status_effect(
            "character_post_defend",
            attack_status=defend_status,
            opponent_attack=opponent_attack,
        )
        return 0

    def equip(self, item: "Item") -> Item | None:
        if (
            self.can_equip(item)
            and self.equipped.add(item) is not None
            and isinstance(item, CanEquip)
        ):
            item.on_equip(player=self, opponent=self.opponent)
            return item
        return None

    def unequip(self, item: "Item") -> Item | None:
        if (
            self.can_unequip(item)
            and self.equipped.remove(item) is not None
            and isinstance(item, CanEquip)
        ):
            item.on_unequip(player=self, opponent=self.opponent)
            return item
        return None

    def consume(self, item: "Item") -> Item | None:
        if self.can_consume(item) and isinstance(item, CanConsume):
            item.on_consume(player=self, opponent=self.opponent)
            return item
        return None

    def apply(self, item: "Item") -> Item | None:
        if (
            self.can_apply(item)
            and self.status_effect.add(item) is not None
            and isinstance(item, IsStatus)
        ):
            item.on_apply(player=self, opponent=self.opponent)
            return item
        return None

    def unapply(self, item: "Item") -> Item | None:
        if (
            self.can_unapply(item)
            and self.status_effect.remove(item) is not None
            and isinstance(item, IsStatus)
        ):
            item.on_unapply(player=self, opponent=self.opponent)
            return item
        return None

    def invoke_status_effect(self, stage: str, **kwargs) -> Any:
        for status_effect in self.status_effect.group.values():
            if isinstance(status_effect, IsStatus):
                status_effect.on(self, self.opponent, stage, **kwargs)

    def _chance(self):
        _max = 100 - self.stat.luck if self.stat.luck < 99 else 99
        return random.randint(0, _max)

    def _attack_status(self) -> AttackStatus:
        if self.can_attack():
            if any(
                [
                    item.can_attack(self, self.opponent)
                    for item in self.equipped.get_items_that_can_attack().values()
                ]
            ):
                return AttackStatus.ATTACK_SUCCESS
            return AttackStatus.ATTACK_NOT_POSSIBLE
        return AttackStatus.ATTACK_MISSED

    def _defend_status(self) -> DefendStatus:
        if not self.can_evade():
            if self.can_defend():
                if any(
                    [
                        item.can_defend(self, self.opponent)
                        for item in self.equipped.get_items_that_can_defend().values()
                    ]
                ):
                    return DefendStatus.DEFEND_SUCCESS
                return DefendStatus.DEFEND_NOT_POSSIBLE
            return DefendStatus.DEFEND_FAILED
        return DefendStatus.ATTACK_EVADED

    def _take_damage(self, damage: int):
        if damage > 0:
            self.stat.health -= damage


class Battle:
    def __init__(self, player: Character, opponent: Character) -> None:
        self.player = player
        self.opponent = opponent

    def initiate(self):
        self.player.initiate_battle(self.opponent)
        self.opponent.initiate_battle(self.player)
