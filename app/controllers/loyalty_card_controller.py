from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DTO.loyalty_card_dto import (
    LoyaltyCardCreateDTO,
    LoyaltyCardResponseDTO
)


class LoyaltyCardController:
    def __init__(self):
        """Initialize the controller with Repository instance"""
        self.repo = LoyaltyCardRepository()

    async def create_loyalty_card(self, card_dto: LoyaltyCardCreateDTO) -> LoyaltyCardResponseDTO:
        created_dao = await self.repo.create_loyalty_card(card_dto)
        return LoyaltyCardResponseDTO.model_validate(created_dao)

    async def attach_loyalty_card_to_customer(
        self,
        card_id: int,
        customer_id: int
    ) -> LoyaltyCardResponseDTO:
        updated_dao = await self.repo.attach_loyalty_card_to_customer(card_id, customer_id)
        return LoyaltyCardResponseDTO.model_validate(updated_dao)

    async def add_points(self, card_id: str, points: int) -> LoyaltyCardResponseDTO:
        updated_dao = await self.repo.add_points(card_id, points)
        return LoyaltyCardResponseDTO.model_validate(updated_dao)
