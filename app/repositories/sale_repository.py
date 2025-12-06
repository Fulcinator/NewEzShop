from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DAO.sale_product_association import SaleProductAssociation
from app.models.DTO.saleTransaction_dto import SaleTransactionDTO
from app.models.DTO.sale_product_association_dto import SaleProductAssociationDTO


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_sale(self, sale_data: dict) -> SaleTransactionDAO:
        sale = SaleTransactionDAO(**sale_data)
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def get_sale_by_id(self, sale_id: int) -> Optional[SaleTransactionDAO]:
        return self.db.query(SaleTransactionDAO).filter(
            SaleTransactionDAO.id == sale_id
        ).first()

    def get_all_sales(self) -> List[SaleTransactionDAO]:
        return self.db.query(SaleTransactionDAO).all()

    def update_sale(self, sale_id: int, update_data: dict) -> Optional[SaleTransactionDAO]:
        sale = self.get_sale_by_id(sale_id)
        if sale:
            for key, value in update_data.items():
                setattr(sale, key, value)
            self.db.commit()
            self.db.refresh(sale)
        return sale

    def delete_sale(self, sale_id: int) -> bool:
        sale = self.get_sale_by_id(sale_id)
        if sale:
            self.db.delete(sale)
            self.db.commit()
            return True
        return False

    def add_line_item(self, sale_id: int, line_data: dict) -> Optional[SaleProductAssociation]:
        line = SaleProductAssociation(sale_transaction_id=sale_id, **line_data)
        self.db.add(line)
        self.db.commit()
        self.db.refresh(line)
        return line

    def get_line_items(self, sale_id: int) -> List[SaleProductAssociation]:
        return self.db.query(SaleProductAssociation).filter(
            SaleProductAssociation.sale_transaction_id == sale_id
        ).all()

    def remove_line_item(self, line_id: int) -> bool:
        line = self.db.query(SaleProductAssociation).filter(
            SaleProductAssociation.id == line_id
        ).first()
        if line:
            self.db.delete(line)
            self.db.commit()
            return True
        return False

    def update_sale_status(self, sale_id: int, status: str) -> Optional[SaleTransactionDAO]:
        return self.update_sale(sale_id, {"status": status})

    def close_sale(self, sale_id: int) -> Optional[SaleTransactionDAO]:
        from datetime import datetime
        return self.update_sale(sale_id, {"status": "PENDING", "closed_at": datetime.utcnow()})

    def apply_discount(self, sale_id: int, discount_rate: float) -> Optional[SaleTransactionDAO]:
        return self.update_sale(sale_id, {"discount_rate": discount_rate})

    def apply_product_discount(self, sale_id: int, product_barcode: str, discount_rate: float) -> Optional[SaleProductAssociation]:
        line = self.db.query(SaleProductAssociation).filter(
            SaleProductAssociation.sale_transaction_id == sale_id
        ).filter(
            SaleProductAssociation.product_barcode == product_barcode
        ).first()
        
        if line:
            line.discount_rate = discount_rate
            self.db.commit()
            self.db.refresh(line)
        return line

    def pay_sale(self, sale_id: int, cash_amount: float) -> tuple[Optional[SaleTransactionDAO], float]:
        from datetime import datetime
        sale = self.get_sale_by_id(sale_id)
        
        if not sale:
            return None, 0.0
        
        # Calculate total amount to pay: sum of all line items with their individual discounts
        total_amount = 0.0
        for line in sale.sale_lines:
            line_total = line.quantity * line.unit_price
            line_amount_after_discount = line_total * (1 - line.discount_rate)
            total_amount += line_amount_after_discount
        
        # Apply sale-level discount
        total_amount = total_amount * (1 - sale.discount_rate)
        
        # Calculate change
        change = cash_amount - total_amount
        
        # Update sale status to PAID and set closed_at timestamp
        sale.status = "PAID"
        sale.closed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sale)
        
        return sale, change

    def compute_points(self, sale_id: int) -> int:
        sale = self.get_sale_by_id(sale_id)
        
        if not sale:
            return 0
        
        # Calculate total paid amount: sum of all line items with their individual discounts
        total_amount = 0.0
        for line in sale.sale_lines:
            line_total = line.quantity * line.unit_price
            line_amount_after_discount = line_total * (1 - line.discount_rate)
            total_amount += line_amount_after_discount
        
        # Apply sale-level discount
        total_amount = total_amount * (1 - sale.discount_rate)
        
        # Calculate points: 1 point per 10 euros (floor division)
        points = int(total_amount / 10)
        
        return points
