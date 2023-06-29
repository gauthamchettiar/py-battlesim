from app.base import *


class ItemCanEquip(Item, CanEquip):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanEquip.__init__(self, **kwargs)


class ItemCanConsume(Item, CanConsume):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanConsume.__init__(self, **kwargs)


class ItemCanAttack(Item, CanAttack):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanAttack.__init__(self, **kwargs)


class ItemCanDefend(Item, CanDefend):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanDefend.__init__(self, **kwargs)


class ItemWeapon(Item, CanAttack, CanEquip):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanAttack.__init__(self, **kwargs)
        CanEquip.__init__(self, **kwargs)


class ItemShield(Item, CanDefend, CanEquip):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        CanDefend.__init__(self, **kwargs)
        CanEquip.__init__(self, **kwargs)


class ItemStatus(Item, IsStatus):
    def __init__(self, **kwargs) -> None:
        Item.__init__(self, **kwargs)
        IsStatus.__init__(self, **kwargs)
