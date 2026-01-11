class FakeLoyaltyCard:
    def __init__(self, id=1):
        self.id = id
        self.customer_id = None


class FakeLoyaltyCardRepository:
    def __init__(self):
        self.cards = {1: FakeLoyaltyCard(1)}

    async def attach_loyalty_card_to_customer(self, card_id, customer_id):
        card = self.cards.get(card_id)
        if card:
            card.customer_id = customer_id
        return card