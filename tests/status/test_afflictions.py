import random
from unittest import TestCase
from tests._artifacts import *
from app.base import *
from app.status.afflictions.poisonous import *
from app.status.afflictions.elemental import *

random.seed(0)


class TestTurnBasedAfflictions(TestCase):
    def setUp(self) -> None:
        Context.current_phase = Phase.BATTLE_NOT_STARTED
        self.player: Character | None = Character(**TEST_INPUT["player"])
        self.opponent: Character | None = Character()
        self.battle: Battle | None = Battle(self.player, self.opponent)

    def tearDown(self) -> None:
        self.player = None
        self.opponent = None
        self.battle = None

    def test_Poisoned(self):
        status = Poisoned()
        self.assertTrue(self.player.can_apply(status))
        self.assertFalse(self.player.can_unapply(status))

        self.assertEqual(self.player.unapply(status), None)
        self.assertEqual(self.player.apply(status), status)
        self.assertEqual(self.player.status_affect.group["Poisoned"], status)

        self.assertTrue(self.player.can_unapply(status))
        for _ in range(6):
            self.battle.switch_to_phase(Phase.TURN_START)
        self.assertEqual(self.player.stat.health, 4)
        self.assertEqual(self.player.unapply(status), status)
        for _ in range(6):
            self.battle.switch_to_phase(Phase.TURN_START)
        self.assertEqual(self.player.stat.health, 4)

    def test_Burning(self):
        status = Burning()

        self.assertEqual(self.player.apply(status), status)
        self.assertEqual(self.player.status_affect.group["Burning"], status)
        self.assertEqual(self.player.stat.health, 5)

        self.battle.switch_to_phase(Phase.TURN_START)

        self.assertEqual(self.player.stat.health, 3)
        for _ in range(6):
            self.battle.switch_to_phase(Phase.TURN_START)

        self.assertEqual(self.player.stat.health, 1)
        self.assertEqual(self.player.unapply(status), status)
        for _ in range(6):
            self.battle.switch_to_phase(Phase.TURN_START)
        self.assertEqual(self.player.stat.health, 1)

    def test_Freeze(self):
        status = Freeze()

        self.assertEqual(self.player.apply(status), status)
        self.assertEqual(self.player.status_affect.group["Freeze"], status)
        self.assertEqual(self.player.stat.agility, 0)
        for _ in range(3):
            self.battle.switch_to_phase(Phase.TURN_START)

        self.assertEqual(self.player.stat.agility, 100)

        self.assertEqual(self.player.unapply(status), status)
        for _ in range(6):
            self.battle.switch_to_phase(Phase.TURN_START)
        self.assertEqual(self.player.stat.agility, 100)
