from collections import defaultdict
import random
from attrs import define, field
from attrs import asdict

from typing import Any

# TODO : Add logic for equipment placing - hand, finger1-2 etc.
# TODO : Add logic for StatusEffect/Ability
# TODO : Add logic for crit attack
# TODO : Add logic for weapons to have custom actions


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
    def __init__(self, group: dict[str, Item], **kwargs) -> None:
        self.group = group

    def add(self, item: Item) -> Item | None:
        if item.flavor.name not in self.group:
            self.group[item.flavor.name] = item
            return item
        return None

    def remove(self, item: Item) -> Item | None:
        if item.flavor.name in self.group:
            return self.group.pop(item.flavor.name)
        return None


class CanEquip:
    def __init__(self, **kwargs) -> None:
        self.stat_to_equip = Stat(**kwargs.get("stat_to_equip", {}))
        self.stat_on_equip = Stat(**kwargs.get("stat_on_equip", {}))

    def can_equip(self, **kwargs) -> bool:
        if (player := kwargs.get("player")) != None and isinstance(player, Character):
            return player.stat >= self.stat_to_equip
        return True

    def can_unequip(self, **kwargs) -> bool:
        return True

    def on_equip(self, **kwargs):
        if (player := kwargs.get("player")) != None and isinstance(player, Character):
            player.stat += self.stat_on_equip

    def on_unequip(self, **kwargs):
        if (player := kwargs.get("player")) != None and isinstance(player, Character):
            player.stat -= self.stat_on_equip


class CanConsume:
    def __init__(self, **kwargs) -> None:
        self.stat_to_consume = Stat(**kwargs.get("stat_to_consume", {}))
        self.stat_on_consume = Stat(**kwargs.get("stat_on_consume", {}))

    def can_consume(self, **kwargs) -> bool:
        if (player := kwargs.get("player")) != None and isinstance(player, Character):
            return player.stat >= self.stat_to_consume
        return True

    def on_consume(self, **kwargs):
        if (player := kwargs.get("player")) != None and isinstance(player, Character):
            player.stat += self.stat_on_consume


class CanAttack:
    def __init__(self, **kwargs) -> None:
        self.stat_on_attack = Stat(**kwargs.get("stat_on_attack", {}))

    def can_attack(self, **kwargs) -> bool:
        return True

    def can_crit(self, **kwargs) -> bool:
        return False

    def pre_attack(self, **kwargs):
        if (player := kwargs.get("player", None)) != None and isinstance(
            player, Character
        ):
            player.stat += self.stat_on_attack

    def post_attack(self, **kwargs):
        if (player := kwargs.get("player", None)) != None and isinstance(
            player, Character
        ):
            player.stat -= self.stat_on_attack

    def on_attack(self, **kwargs) -> int:
        if (
            (player := kwargs.get("player", None)) != None
            and isinstance(player, Character)
        ) and (
            (opponent := kwargs.get("opponent", None)) != None
            and isinstance(opponent, Character)
        ):
            self.pre_attack(**kwargs)
            damage_done = opponent.defend(**kwargs)
            self.post_attack(damage_done=damage_done, **kwargs)
            return damage_done
        return 0


class CanDefend:
    def __init__(self, **kwargs) -> None:
        self.stat_on_defend = Stat(**kwargs.get("stat_on_defend", {}))

    def can_defend(self, **kwargs):
        return True

    def can_evade(self, **kwargs) -> bool:
        return False

    def pre_defend(self, **kwargs):
        if (player := kwargs.get("player", None)) != None and isinstance(
            player, Character
        ):
            player.stat += self.stat_on_defend

    def post_defend(self, **kwargs):
        if (player := kwargs.get("player", None)) != None and isinstance(
            player, Character
        ):
            player.stat -= self.stat_on_defend


class Character:
    def __init__(self, **kwargs) -> None:
        self.flavor = FlavorStat(**kwargs.get("flavor", {}))
        self.stat = Stat(**kwargs.get("stat", {}))
        self.equipped = ItemGroup(group={})
        self.opponent: Character | None = None

    def initiate_battle(self, opponent: "Character"):
        self.opponent = opponent

    def can_attack(self, **kwargs) -> bool:
        return self.stat.agility >= self._chance

    def can_crit(self, **kwargs) -> bool:
        return False

    def can_evade(self, **kwargs) -> bool:
        return self.stat.agility >= self._chance

    def can_defend(self, **kwargs) -> bool:
        return True

    def attack(self, **kwargs) -> int:
        if self.can_attack(**kwargs):
            damage_done = 0
            for item in self.equipped.group.values():
                if isinstance(item, CanAttack) and item.can_attack(
                    player=self, opponent=self.opponent, **kwargs
                ):
                    damage_done += item.on_attack(
                        player=self, opponent=self.opponent, **kwargs
                    )
            return damage_done
        return 0

    def defend(self, **kwargs) -> int:
        if not self.can_evade(**kwargs):
            damage_taken = (
                self.opponent.stat.attack if isinstance(self.opponent, Character) else 0
            )
            if self.can_defend(**kwargs):
                defendable_items = [
                    item
                    for item in self.equipped.group.values()
                    if isinstance(item, CanDefend) and item.can_defend(**kwargs)
                ]

                for item in defendable_items:
                    item.pre_defend(**dict(kwargs, player=self, opponent=self.opponent))

                damage_taken -= self.stat.defense if len(defendable_items) > 0 else 0

                self.take_damage(damage_taken)

                for item in defendable_items:
                    item.post_defend(
                        **dict(kwargs, player=self, opponent=self.opponent)
                    )
            else:
                self.take_damage(damage_taken)
            return damage_taken
        return 0

    def take_damage(self, damage: int):
        if damage > 0:
            self.stat.health -= damage

    def can_equip(self, item: "Item", **kwargs) -> bool:
        if isinstance(item, Item) and isinstance(item, CanEquip):
            return item.can_equip(player=self, opponent=self.opponent, **kwargs)
        return False

    def can_unequip(self, item: "Item", **kwargs) -> bool:
        if isinstance(item, Item) and isinstance(item, CanEquip):
            return item.can_unequip(player=self, opponent=self.opponent, **kwargs)
        return False

    def equip(self, item: "Item", **kwargs) -> Item | None:
        if self.can_equip(item, **kwargs):
            if (equipped_item := self.equipped.add(item)) != None:
                if isinstance(item, Item) and isinstance(item, CanEquip):
                    item.on_equip(player=self, opponent=self.opponent, **kwargs)
                    return equipped_item
        return None

    def unequip(self, item: "Item", **kwargs) -> Item | None:
        if self.can_unequip(item, **kwargs):
            if (unequipped_item := self.equipped.remove(item)) != None:
                if isinstance(item, Item) and isinstance(item, CanEquip):
                    item.on_unequip(player=self, opponent=self.opponent, **kwargs)
                    return unequipped_item
        return None

    def can_consume(self, item: "Item", **kwargs) -> bool:
        if isinstance(item, Item) and isinstance(item, CanConsume):
            return item.can_consume(player=self, opponent=self.opponent, **kwargs)
        return False

    def consume(self, item: "Item", **kwargs) -> Item | None:
        if self.can_consume(item, **kwargs):
            if isinstance(item, Item) and isinstance(item, CanConsume):
                item.on_consume(player=self, opponent=self.opponent, **kwargs)
                return item
        return None

    @property
    def _chance(self):
        _max = 100 - self.stat.luck if self.stat.luck < 99 else 99
        return random.randint(0, _max)


class Battle:
    def __init__(self, player: Character, opponent: Character) -> None:
        self.player = player
        self.opponent = opponent

    def initiate(self):
        self.player.initiate_battle(self.opponent)
        self.opponent.initiate_battle(self.player)
