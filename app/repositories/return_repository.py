from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.DAO.returnTransaction_dao import ReturnTransactionDAO
from app.models.DAO.return_product_association import ReturnProductAssociation
from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO
from app.models.DTO.return_product_association_dto import ReturnProductAssociationDTO


class ReturnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_return(self, return_data: dict) -> ReturnTransactionDAO:
        return_obj = ReturnTransactionDAO(**return_data)
        self.db.add(return_obj)
        self.db.commit()
        self.db.refresh(return_obj)
        return return_obj

    def get_return_by_id(self, return_id: int) -> Optional[ReturnTransactionDAO]:
        return self.db.query(ReturnTransactionDAO).filter(
            ReturnTransactionDAO.id == return_id
        ).first()

    def get_all_returns(self) -> List[ReturnTransactionDAO]:
        return self.db.query(ReturnTransactionDAO).all()

    def get_returns_by_sale_id(self, sale_id: int) -> List[ReturnTransactionDAO]:
        return self.db.query(ReturnTransactionDAO).filter(
            ReturnTransactionDAO.sale_transaction_id == sale_id
        ).all()

    def update_return(self, return_id: int, update_data: dict) -> Optional[ReturnTransactionDAO]:
        return_obj = self.get_return_by_id(return_id)
        if return_obj:
            for key, value in update_data.items():
                setattr(return_obj, key, value)
            self.db.commit()
            self.db.refresh(return_obj)
        return return_obj

    def delete_return(self, return_id: int) -> bool:
        return_obj = self.get_return_by_id(return_id)
        if return_obj:
            self.db.delete(return_obj)
            self.db.commit()
            return True
        return False

    def add_returned_product(self, return_id: int, product_data: dict) -> Optional[ReturnProductAssociation]:
        product = ReturnProductAssociation(return_transaction_id=return_id, **product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_returned_products(self, return_id: int) -> List[ReturnProductAssociation]:
        return self.db.query(ReturnProductAssociation).filter(
            ReturnProductAssociation.return_transaction_id == return_id
        ).all()

    def remove_returned_product(self, product_id: int) -> bool:
        product = self.db.query(ReturnProductAssociation).filter(
            ReturnProductAssociation.id == product_id
        ).first()
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False

    def update_return_status(self, return_id: int, status: str) -> Optional[ReturnTransactionDAO]:
        return self.update_return(return_id, {"status": status})

    def close_return(self, return_id: int) -> Optional[ReturnTransactionDAO]:
        from datetime import datetime
        return self.update_return(return_id, {"status": "CLOSED", "closed_at": datetime.utcnow()})

    def mark_reimbursed(self, return_id: int) -> Optional[ReturnTransactionDAO]:
        return self.update_return(return_id, {"status": "REIMBURSED"})
