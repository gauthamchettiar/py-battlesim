from unittest import TestCase

from app.base import Character, Battle
from app.items.weapons.swords import *


class TestSwords(TestCase):
    def setUp(self) -> None:
        self.player: Character | None = Character(stat={"agility": 100})
        self.opponent: Character | None = Character()
        self.battle: Battle | None = Battle(self.player, self.opponent)

        self.battle.initiate()

    def tearDown(self) -> None:
        self.player, self.opponent = None, None
        self.battle = None

    def test_RustedSword(self):
        sword = RustedSword()
        self.player.stat.strength = sword.stat_to_equip.strength
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
        self.assertEqual(self.player.attack(), 8)

    def test_IronSword(self):
        sword = IronSword()
        self.player.stat.strength = sword.stat_to_equip.strength
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
        self.assertEqual(self.player.attack(), 12)

    def test_SilverSword(self):
        sword = SilverSword()
        self.player.stat.strength = sword.stat_to_equip.strength
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
        self.assertEqual(self.player.attack(), 18)

    def test_FlameSword(self):
        sword = FlameSword()
        self.player.stat.strength = sword.stat_to_equip.strength
        self.player.stat.intelligence = sword.stat_to_equip.intelligence
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
        self.assertEqual(self.player.attack(), 18)
        self.opponent.flavor.category = "UNDEAD"
        self.assertEqual(self.player.attack(), 36)
        self.assertTrue(
            isinstance(
                self.opponent.status_effect.group[Burning().flavor.name], Burning
            )
        )

    def test_FrostSword(self):
        sword = FrostSword()
        self.player.stat.strength = sword.stat_to_equip.strength
        self.player.stat.intelligence = sword.stat_to_equip.intelligence
        self.player.equip(sword)
        self.assertTrue(sword.flavor.name in self.player.equipped.group)
        self.assertEqual(self.player.stat.attack, 0)
        self.assertEqual(self.player.attack(), 14)
        self.assertEqual(self.player.attack(), 14)
        self.assertTrue(
            isinstance(self.opponent.status_effect.group[Freeze().flavor.name], Freeze)
        )
