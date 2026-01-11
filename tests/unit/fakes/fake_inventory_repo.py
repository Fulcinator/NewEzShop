class FakePosition:
    def __init__(self, aisleID=None, rackID=None, levelID=None):
        self.id = None
        self.aisleID = aisleID
        self.rackID = rackID
        self.levelID = levelID


class FakeProductType:
    def __init__(
        self,
        id,
        barcode="1234567890123",
        name="Test Product",
        description="Test Description",
        sellPrice=10.0,
        quantity=10,
        discountRate=0.0,
        notes=None,
        aisleID=None,
        rackID=None,
        levelID=None
    ):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.description = description
        self.sellPrice = sellPrice
        self.quantity = quantity
        self.discountRate = discountRate
        self.notes = notes

        # posizione simulata
        self.position = FakePosition(aisleID, rackID, levelID)

class FakeInventoryRepository:
    def __init__(self):
        self.items = {
            1: FakeProductType(id=1, quantity=10),
            2: FakeProductType(id=2, quantity=5),
        }

    async def update_quantity(self, product_type_id: int, new_quantity: int):
        pt = self.items.get(product_type_id)
        if not pt:
            raise ValueError("ProductType not found")
        pt.quantity = new_quantity
        return pt

    async def update_position(self, product_type_id: int, aisleID, rackID, levelID):
        pt = self.items.get(product_type_id)
        if not pt:
            raise ValueError("ProductType not found")
        pt.position.aisleID = aisleID
        pt.position.rackID = rackID
        pt.position.levelID = levelID
        return pt