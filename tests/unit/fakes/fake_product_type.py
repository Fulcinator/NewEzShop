class FakeProductTypeDAO:
    def __init__(
        self,
        id=1,
        barcode="123",
        name="Milk",
        description=None,
        sellPrice=1.5,
        quantity=10,
        discountRate=None,
        notes=None,
        position=None,
    ):
        self.id = id
        self.barcode = barcode
        self.name = name
        self.description = description
        self.sellPrice = sellPrice
        self.quantity = quantity
        self.discountRate = discountRate
        self.notes = notes
        self.position = position


class FakeProductTypeRepository:
    def __init__(self):
        self.product = None

    async def create_product_type(self, dto):
        return FakeProductTypeDAO(
            barcode=dto.barcode,
            name=dto.name,
            description=dto.description,
            sellPrice=dto.sellPrice,
            quantity=dto.quantity,
            discountRate=dto.discountRate,
            notes=dto.notes,
            position=None
        )

    async def update_product_type(self, id, dto):
        return FakeProductTypeDAO(
            id=id,
            barcode=dto.barcode or "123",
            name=dto.name or "Milk",
            description=dto.description,
            sellPrice=dto.sellPrice or 2.0,
            quantity=dto.quantity or 10,
            discountRate=dto.discountRate,
            notes=dto.notes,
            position=None
        )


    async def delete_product_type(self, id):
        self.product = None
        return True

    async def list_product_types(self):
        return [self.product] if self.product else []

    async def search_product_types(self, barcode=None, description=None):
        if not self.product:
            return []

        if barcode and self.product.barcode != barcode:
            return []

        if description and (
            not self.product.description
            or description not in self.product.description
        ):
            return []

        return [self.product]