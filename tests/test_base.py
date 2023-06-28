from collections.abc import Callable
from copy import deepcopy
from typing import Any
from unittest import TestCase
from app.base import *
from tests._artifacts import *
import random

random.seed(0)

DIC: dict[str, Any] = {
    "player": {
        "flavor": {
            "name": "Player",
            "description": "Player Description",
            "category": "SAMPLE_CAT",
            "sub_category": "SAMPLE_SUBCAT",
            "type": [],
        },
        "stat": {
            "health": 10,
            "attack": 20,
            "defense": 30,
            "strength": 40,
            "intelligence": 50,
            "fatigue": 60,
            "mana": 70,
            "agility": 100,
            "luck": 0,
        },
    },
    "opponent": {
        "flavor": {
            "name": "Opponent",
            "description": "Opponent Description",
            "category": "SAMPLE_CAT2",
            "sub_category": "SAMPLE_SUBCAT2",
            "type": [],
        },
        "stat": {
            "health": 9,
            "attack": 19,
            "defense": 29,
            "strength": 39,
            "intelligence": 49,
            "fatigue": 59,
            "mana": 69,
            "agility": 0,
            "luck": -1,
        },
    },
    "item_can_equip": {
        "flavor": {"name": "item_can_equip"},
        "stat_to_equip": {
            "health": 10,
            "attack": 20,
            "defense": 30,
            "strength": 40,
            "intelligence": 50,
            "fatigue": 60,
            "mana": 70,
            "agility": 100,
            "luck": 0,
        },
        "stat_on_equip": {
            "health": 1,
            "attack": 2,
            "defense": 3,
            "strength": 4,
            "intelligence": 5,
            "fatigue": 6,
            "mana": 7,
            "agility": 8,
            "luck": 9,
        },
    },
    "item_can_consume": {
        "stat_on_consume": {
            "health": 0,
            "attack": 1,
            "defense": 2,
            "strength": 3,
            "intelligence": 4,
            "fatigue": 5,
            "mana": 6,
            "agility": 7,
            "luck": 8,
        },
    },
    "item_can_attack": {
        "stat_on_attack": {
            "health": 11,
            "attack": 22,
            "defense": 33,
            "strength": 44,
            "intelligence": 55,
            "fatigue": 66,
            "mana": 77,
            "agility": 88,
            "luck": 99,
        },
    },
    "item_can_defend": {
        "stat_on_defend": {
            "health": 0,
            "attack": 7,
            "defense": 6,
            "strength": 5,
            "intelligence": 4,
            "fatigue": 3,
            "mana": 2,
            "agility": 1,
            "luck": 0,
        },
    },
}


class TestCharacter(TestCase):
    def setUp(self) -> None:
        self.player: Character | None = Character(**DIC["player"])
        self.opponent: Character | None = Character(**DIC["opponent"])
        self.item_can_equip: ItemCanEquip | None = ItemCanEquip(**DIC["item_can_equip"])
        self.item_can_consume: ItemCanConsume | None = ItemCanConsume(
            **DIC["item_can_consume"]
        )
        self.item_weapon: ItemWeapon | None = ItemWeapon(
            **DIC["item_can_equip"], **DIC["item_can_attack"]
        )
        self.item_shield: ItemShield | None = ItemShield(
            **DIC["item_can_equip"], **DIC["item_can_defend"]
        )
        self.battle: Battle | None = Battle(self.player, self.opponent)

    def tearDown(self) -> None:
        self.player, self.opponent = None, None
        self.item_can_equip, self.item_can_consume = None, None
        self.item_weapon, self.item_shield = None, None
        self.battle = None

    def test_stat(self):
        self.assertEqual(self.player.stat.to_dict(), DIC["player"]["stat"])
        self.assertEqual(self.player.flavor.to_dict(), DIC["player"]["flavor"])
        self.assertTrue(self.player.stat.is_alive)

    def test_equip_unequip(self):
        item_can_equip2 = deepcopy(self.item_can_equip)
        item_can_equip2.flavor.name = "item_can_equip2"

        item_can_equip3 = deepcopy(self.item_can_equip)
        item_can_equip3.flavor.name = "item_can_equip3"
        item_can_equip3.stat_to_equip.strength = 41

        self.assertEqual(self.player.equip(item_can_equip3), None)
        self.assertEqual(self.player.equip(self.item_can_equip), self.item_can_equip)
        self.assertEqual(self.player.equip(self.item_can_equip), None)
        self.assertEqual(self.player.equip(item_can_equip2), item_can_equip2)

        self.assertEqual(
            self.player.equipped.group,
            {
                self.item_can_equip.flavor.name: self.item_can_equip,
                item_can_equip2.flavor.name: item_can_equip2,
            },
        )
        self.assertEqual(self.player.equip(self.item_can_consume), None)

        self.assertEqual(
            self.player.stat.to_dict(),
            {
                "agility": 116,
                "attack": 24,
                "defense": 36,
                "fatigue": 72,
                "health": 12,
                "intelligence": 60,
                "luck": 18,
                "mana": 84,
                "strength": 48,
            },
        )

        self.assertEqual(self.player.unequip(self.item_can_equip), self.item_can_equip)
        self.assertEqual(self.player.unequip(self.item_can_equip), None)
        self.assertEqual(self.player.unequip(self.item_can_consume), None)
        self.assertEqual(
            self.player.equipped.group,
            {item_can_equip2.flavor.name: item_can_equip2},
        )

        self.assertEqual(
            self.player.stat.to_dict(),
            {
                "agility": 108,
                "attack": 22,
                "defense": 33,
                "fatigue": 66,
                "health": 11,
                "intelligence": 55,
                "luck": 9,
                "mana": 77,
                "strength": 44,
            },
        )

    def test_consume(self):
        item_can_consume2 = deepcopy(self.item_can_consume)
        item_can_consume2.flavor.name = "item_can_consume2"

        item_can_consume3 = deepcopy(self.item_can_consume)
        item_can_consume3.flavor.name = "item_can_consume3"
        item_can_consume3.stat_to_consume.intelligence = 51

        self.assertEqual(self.player.consume(item_can_consume3), None)
        self.assertEqual(
            self.player.consume(self.item_can_consume), self.item_can_consume
        )
        self.assertEqual(self.player.consume(item_can_consume2), item_can_consume2)
        self.assertEqual(self.player.consume(self.item_can_equip), None)

        self.assertEqual(
            self.player.stat.to_dict(),
            {
                "agility": 114,
                "attack": 22,
                "defense": 34,
                "fatigue": 70,
                "health": 10,
                "intelligence": 58,
                "luck": 16,
                "mana": 82,
                "strength": 46,
            },
        )

    def test_attack_defend(self):
        self.assertTrue(self.player.can_attack())
        self.assertFalse(self.player.can_crit())

        self.assertEqual(self.player.attack(), 0)

        self.battle.initiate()

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.equip(self.item_weapon), self.item_weapon)
        self.assertEqual(
            self.player.attack(),
            (
                damage1 := DIC["player"]["stat"]["attack"]
                + DIC["item_can_equip"]["stat_on_equip"]["attack"]
                + DIC["item_can_attack"]["stat_on_attack"]["attack"]
            ),
        )
        self.assertEqual(
            self.opponent.stat.health,
            (health1 := DIC["opponent"]["stat"]["health"] - damage1),
        )

        self.item_shield.stat_to_equip = Stat(
            **{k: -99 for k in self.item_shield.stat_to_equip.to_dict().keys()}
        )

        self.assertEqual(self.opponent.equip(self.item_shield), self.item_shield)
        self.assertEqual(
            self.opponent.stat.health,
            (health1 := health1 + DIC["item_can_equip"]["stat_on_equip"]["health"]),
        )
        self.assertEqual(
            self.player.attack(),
            (
                damage2 := damage1
                - (
                    DIC["opponent"]["stat"]["defense"]
                    + DIC["item_can_equip"]["stat_on_equip"]["defense"]
                    + DIC["item_can_defend"]["stat_on_defend"]["defense"]
                )
            ),
        )
        self.assertEqual(
            self.opponent.stat.health,
            (health2 := health1 - damage2),
        )

        self.player.can_attack = lambda: False
        self.assertEqual(self.player.attack(), 0)
        self.player.can_attack = lambda: True

        self.opponent.can_defend = lambda: False
        self.assertEqual(self.player.attack(), damage1)
        self.opponent.can_defend = lambda: True

        self.opponent.can_evade = lambda: True
        self.assertEqual(self.player.attack(), 0)

    def test_crit_damage(self):
        self.battle.initiate()
        self.player.can_crit = lambda: True
        self.assertEqual(self.player.equip(self.item_weapon), self.item_weapon)

        self.assertEqual(
            self.player.attack(),
            (
                damage1 := (
                    DIC["player"]["stat"]["attack"]
                    + DIC["item_can_equip"]["stat_on_equip"]["attack"]
                    + DIC["item_can_attack"]["stat_on_attack"]["attack"]
                )
                * 2
            ),
        )
