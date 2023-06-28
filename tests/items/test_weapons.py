from unittest import TestCase

from app.base import Character
from app.items.weapons.swords import *


class TestSwords(TestCase):
    def setUp(self) -> None:
        self.player: Character | None = Character()

    def tearDown(self) -> None:
        self.player = None

    def test_RustedSword(self):
        sword = RustedSword()
        self.player.stat.strength = 15
        self.assertEqual(self.player.stat.attack, 0)
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
