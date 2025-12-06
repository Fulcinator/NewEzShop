from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repositories.sale_repository import SaleRepository
from app.services.mapper_service import simple_map
from app.models.DTO.saleTransaction_dto import SaleTransactionDTO
from app.models.DTO.sale_product_association_dto import SaleProductAssociationDTO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO


class SaleController:
    def __init__(self, db: Session):
        self.repo = SaleRepository(db)

    def start_sale(self) -> SaleTransactionDTO:
        sale_data = {
            "status": "OPEN",
            "discount_rate": 0.0,
            "cost": 0.0
        }
        dao = self.repo.create_sale(sale_data)
        return simple_map(dao, SaleTransactionDTO)

    def get_all_sales(self) -> List[SaleTransactionDTO]:
        daos = self.repo.get_all_sales()
        return [simple_map(d, SaleTransactionDTO) for d in daos]

    def get_sale(self, sale_id: int) -> Optional[SaleTransactionDTO]:
        dao = self.repo.get_sale_by_id(sale_id)
        if dao:
            return simple_map(dao, SaleTransactionDTO)
        return None

    def delete_sale(self, sale_id: int) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        if sale and sale.status != "PAID":
            return self.repo.delete_sale(sale_id)
        return False

    def add_product_to_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is OPEN
        if not sale or sale.status != "OPEN":
            return False
        
        # Check amount is positive
        if amount <= 0:
            return False
        
        # Check product exists by barcode and has sufficient quantity
        product = self.repo.db.query(ProductTypeDAO).filter(
            ProductTypeDAO.barcode == barcode
        ).first()
        
        if not product:
            # Product not found
            return False
        
        if product.quantity < amount:
            # Insufficient quantity
            return False
        
        # Decrease product quantity
        product.quantity -= amount
        
        line_data = {
            "product_type_id": product.id,
            "product_barcode": barcode,
            "quantity": amount,
            "unit_price": product.sellPrice,
            "discount_rate": 0.0
        }
        
        self.repo.add_line_item(sale_id, line_data)
        self.repo.db.commit()
        return True

    def remove_product_from_sale(self, sale_id: int, barcode: str, amount: int) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is OPEN
        if not sale or sale.status != "OPEN":
            return False
        
        # Get the product by barcode
        product = self.repo.db.query(ProductTypeDAO).filter(
            ProductTypeDAO.barcode == barcode
        ).first()
        
        if not product:
            return False
        
        # Get the line item
        lines = self.repo.get_line_items(sale_id)
        for line in lines:
            if line.product_type_id == product.id:
                if amount >= line.quantity:
                    # Remove completely and restore inventory
                    product.quantity += line.quantity
                    self.repo.remove_line_item(line.id)
                else:
                    # Decrease quantity and restore partial inventory
                    product.quantity += amount
                    line.quantity -= amount
                    self.repo.db.commit()
                return True
        
        return False

    def apply_discount_to_sale(self, sale_id: int, discount_rate: float) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is OPEN
        if not sale or sale.status != "OPEN":
            return False
        
        # Validate discount rate
        if discount_rate < 0.0 or discount_rate > 1.0:
            return False
        
        self.repo.apply_discount(sale_id, discount_rate)
        return True

    def apply_discount_to_product(self, sale_id: int, product_barcode: str, discount_rate: float) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is OPEN
        if not sale or sale.status != "OPEN":
            return False
        
        # Validate discount rate
        if discount_rate < 0.0 or discount_rate > 1.0:
            return False
        
        # Get the product by barcode
        product = self.repo.db.query(ProductTypeDAO).filter(
            ProductTypeDAO.barcode == product_barcode
        ).first()
        
        if not product:
            return False
        
        # Find and update the line item
        lines = self.repo.get_line_items(sale_id)
        for line in lines:
            if line.product_type_id == product.id:
                line.discount_rate = discount_rate
                self.repo.db.commit()
                self.repo.db.refresh(line)
                return True
        
        return False

    def close_sale(self, sale_id: int) -> bool:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is OPEN
        if not sale or sale.status != "OPEN":
            return False
        
        self.repo.close_sale(sale_id)
        return True

    def pay_sale(self, sale_id: int, cash_amount: float) -> Optional[dict]:
        sale = self.repo.get_sale_by_id(sale_id)
        
        # Check sale is PENDING
        if not sale or sale.status != "PENDING":
            return None
        
        updated_sale, change = self.repo.pay_sale(sale_id, cash_amount)
        
        if updated_sale:
            # Calculate sale total amount
            total_amount = 0.0
            for line in updated_sale.sale_lines:
                line_total = line.quantity * line.unit_price
                line_amount_after_discount = line_total * (1 - line.discount_rate)
                total_amount += line_amount_after_discount
            
            # Apply sale-level discount
            total_amount = total_amount * (1 - updated_sale.discount_rate)
            
            # Update shop balance (credit operation - sale payment increases balance)
            system_info = self.repo.db.query(SystemInfoDAO).first()
            if system_info:
                system_info.balance += total_amount
                self.repo.db.commit()
            
            return {"change": round(change, 2)}
        
        return None

    def compute_points(self, sale_id: int) -> Optional[dict]:
        sale = self.repo.get_sale_by_id(sale_id)
        
        if not sale:
            return None
        
        points = self.repo.compute_points(sale_id)
        return {"points": points}
