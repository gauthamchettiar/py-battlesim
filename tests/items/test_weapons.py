import random
from unittest import TestCase
from tests._artifacts import *
from app.base import *
from app.items.weapons.swords import *

random.seed(0)


class TestSwords(TestCase):
    def setUp(self) -> None:
        Context.current_phase = Phase.BATTLE_NOT_STARTED
        self.player: Character | None = Character(**TEST_INPUT["player"])
        self.opponent: Character | None = Character()
        self.battle: Battle | None = Battle(self.player, self.opponent)

    def tearDown(self) -> None:
        self.player = None
        self.opponent = None
        self.battle = None

    def test_RustedSword(self):
        sword = RustedSword()
        self.player.equip(sword)
        self.assertEqual(self.player.equipped.group[sword.flavor.name], sword)
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health, -(self.player.stat.attack + sword.stat.attack)
        )

    def test_IronSword(self):
        sword = IronSword()
        self.player.equip(sword)
        self.assertEqual(self.player.equipped.group[sword.flavor.name], sword)
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health, -(self.player.stat.attack + sword.stat.attack)
        )

    def test_SilverSword(self):
        sword = SilverSword()
        self.player.equip(sword)
        self.assertEqual(self.player.equipped.group[sword.flavor.name], sword)
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health, -(self.player.stat.attack + sword.stat.attack)
        )

    def test_FlameSword(self):
        sword = FlameSword()
        self.player.equip(sword)
        self.assertEqual(self.player.equipped.group[sword.flavor.name], sword)
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health, -(self.player.stat.attack + sword.stat.attack)
        )
        self.opponent.stat.health = 0
        self.opponent.flavor.category = "UNDEAD"
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health,
            -(self.player.stat.attack + (sword.stat.attack * 2)),
        )
        sword.burning_probability = 100
        self.player.perform_item_attack()
        self.assertTrue("Burning" in self.opponent.status_affect.group.keys())
        self.assertEqual(sword.stat.health, 8)

    def test_FrostSword(self):
        sword = FrostSword()
        self.player.equip(sword)
        self.assertEqual(self.player.equipped.group[sword.flavor.name], sword)
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])
        self.player.perform_item_attack()
        self.assertEqual(
            self.opponent.stat.health, -(self.player.stat.attack + sword.stat.attack)
        )
        self.opponent.stat.health = 0

        sword.freeze_probability = 100
        self.player.perform_item_attack()
        self.assertTrue("Freeze" in self.opponent.status_affect.group.keys())
        sword.ice_bolt_freeze_probability = 100
        sword.perform_action("shoot_ice_bolts")
        self.assertEqual(sword.stat.health, 8)
