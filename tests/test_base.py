from copy import deepcopy
from unittest import TestCase
from tests._artifacts import *
from app.base import *
import random

random.seed(0)


class TestCharacter(TestCase):
    def setUp(self) -> None:
        self.player = Character(**TEST_INPUT["player"])
        self.opponent = Character(**TEST_INPUT["opponent"])
        self.battle = Battle(self.player, self.opponent)

        self.item1 = Item(**TEST_INPUT["item"])

    def test_player(self):
        self.assertEqual(Context.current_phase, Phase.BATTLE_NOT_STARTED)
        self.assertEqual(self.player.flavor.to_dict(), TEST_INPUT["player"]["flavor"])
        self.assertEqual(self.player.stat.to_dict(), TEST_INPUT["player"]["stat"])

        self.assertEqual(self.player.opponent, self.opponent)
        self.assertEqual(self.opponent.opponent, self.player)

        self.assertEqual(self.player.defense_by_equipment, 0)
        self.assertEqual(
            self.player.get_available_actions(Phase.PLAYER_ATTACK_START)[
                "perform_item_attack"
            ],
            self.player.perform_item_attack,
        )
        self.assertEqual(
            self.opponent.get_available_actions(Phase.OPPONENT_ATTACK_START)[
                "perform_item_attack"
            ],
            self.opponent.perform_item_attack,
        )

        self.assertEqual(len(self.player.get_available_actions()), 0)

        self.assertTrue(self.player.can_equip(self.item1))
        self.assertEqual(self.player.equip(self.item1), self.item1)

        self.assertTrue(self.player.can_unequip(self.item1))
        self.assertTrue(self.player.can_consume(self.item1))

        self.assertEqual(self.player.consume(self.item1), self.item1)

        self.assertIsNone(self.player.perform_item_attack())

        self.assertEqual(self.opponent.stat.health, -7)  # has been calculated
        self.opponent.heal(16)
        self.assertEqual(self.opponent.stat.health, 9)  # has been calculated

        item2 = deepcopy(self.item1)
        item2.character_can_equip = lambda char: True

        self.assertEqual(self.opponent.equip(item2), item2)

        self.assertEqual(self.player.perform_action("perform_item_attack"), None)
        self.assertEqual(self.opponent.stat.health, 10)  # has been calculated

        self.assertEqual(self.player.unequip(self.item1), self.item1)

        self.assertEqual(self.opponent.equip(self.item1), None)
        self.assertEqual(self.opponent.consume(self.item1), None)
        self.assertEqual(self.opponent.unequip(self.item1), None)
