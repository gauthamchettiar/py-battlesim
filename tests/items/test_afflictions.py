from unittest import TestCase

from app.base import Character, Battle
from app.status.afflictions import *
from tests._artifacts import *


class TestSwords(TestCase):
    def setUp(self) -> None:
        self.player: Character | None = Character(stat={"agility": 100})
        self.opponent: Character | None = Character()
        self.battle: Battle | None = Battle(self.player, self.opponent)
        self.weapon = ItemWeapon()

        self.battle.initiate()

    def test_Poisoned(self):
        affliction = Poisoned()
        self.player.equip(self.weapon)
        self.player.apply(affliction)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -1)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -2)

    def test_Burning(self):
        affliction = Burning()
        self.player.equip(self.weapon)
        self.player.apply(affliction)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -2)
        self.assertEqual(self.player.stat.defense, -1)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -4)
        self.assertEqual(self.player.stat.defense, -2)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -6)
        self.assertEqual(self.player.stat.defense, -3)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.health, -6)
        self.assertEqual(self.player.stat.defense, -3)

    def test_Freeze(self):
        affliction = Freeze()
        self.player.equip(self.weapon)
        self.assertEqual(self.player.stat.agility, 100)

        self.player.apply(affliction)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.agility, 0)

        self.assertEqual(self.player.defend(), 0)
        self.assertEqual(self.player.stat.agility, 0)

        self.assertEqual(self.player.attack(), 0)
        self.assertEqual(self.player.stat.agility, 100)
