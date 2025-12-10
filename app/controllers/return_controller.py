from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.return_repository import ReturnRepository
from app.repositories.sale_repository import SaleRepository
from app.services.mapper_service import simple_map
from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO
from app.models.DTO.return_product_association_dto import ReturnProductAssociationDTO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO


class ReturnController:
    def __init__(self, db: Session):
        self.repo = ReturnRepository(db)

    def start_return(self, sale_id: int) -> Optional[ReturnTransactionDTO]:
        # Verify sale exists and is CLOSED/PAID
        sale = self.repo.db.query(SaleTransactionDAO).filter(
            SaleTransactionDAO.id == sale_id
        ).first()
        
        if not sale or sale.status not in ("PENDING", "PAID"):
            return None
        
        return_data = {
            "sale_transaction_id": sale_id,
            "status": "OPEN",
            "created_at": None  # Will be set by database
        }
        dao = self.repo.create_return(return_data)
        return simple_map(dao, ReturnTransactionDTO)

    def get_all_returns(self) -> List[ReturnTransactionDTO]:
        daos = self.repo.get_all_returns()
        return [simple_map(d, ReturnTransactionDTO) for d in daos]

    def get_return(self, return_id: int) -> Optional[ReturnTransactionDTO]:
        dao = self.repo.get_return_by_id(return_id)
        if dao:
            return simple_map(dao, ReturnTransactionDTO)
        return None

    def get_returns_by_sale(self, sale_id: int) -> List[ReturnTransactionDTO]:
        daos = self.repo.get_returns_by_sale_id(sale_id)
        return [simple_map(d, ReturnTransactionDTO) for d in daos]

    def delete_return(self, return_id: int) -> bool:
        return_obj = self.repo.get_return_by_id(return_id)
        if return_obj and return_obj.status != "REIMBURSED":
            return self.repo.delete_return(return_id)
        return False

    def add_product_to_return(self, return_id: int, barcode: str, amount: int) -> bool:
        return_obj = self.repo.get_return_by_id(return_id)
        
        # Check return is OPEN
        if not return_obj or return_obj.status != "OPEN":
            return False
        
        # Check amount is positive
        if amount <= 0:
            return False
        
        # Get the product by barcode
        product = self.repo.db.query(ProductTypeDAO).filter(
            ProductTypeDAO.barcode == barcode
        ).first()
        
        if not product:
            return False
        
        # Check product was in the original sale and quantity doesn't exceed sold amount
        sale = self.repo.db.query(SaleTransactionDAO).filter(
            SaleTransactionDAO.id == return_obj.sale_transaction_id
        ).first()
        
        if not sale:
            return False
        
        # Find the product in the original sale
        sale_line = None
        for line in sale.sale_lines:
            if line.product_type_id == product.id:
                sale_line = line
                break
        
        if not sale_line or sale_line.quantity < amount:
            return False
        
        product_data = {
            "product_type_id": product.id,
            "quantity": amount
        }
        
        self.repo.add_returned_product(return_id, product_data)
        return True

    def remove_product_from_return(self, return_id: int, barcode: str, amount: int) -> bool:
        return_obj = self.repo.get_return_by_id(return_id)
        
        # Check return is OPEN
        if not return_obj or return_obj.status != "OPEN":
            return False
        
        # Get the product by barcode
        product = self.repo.db.query(ProductTypeDAO).filter(
            ProductTypeDAO.barcode == barcode
        ).first()
        
        if not product:
            return False
        
        # Get the returned product line
        products = self.repo.get_returned_products(return_id)
        for returned_product in products:
            if returned_product.product_type_id == product.id:
                if amount >= returned_product.quantity:
                    # Remove completely
                    self.repo.remove_returned_product(returned_product.id)
                else:
                    # Decrease quantity
                    returned_product.quantity -= amount
                    self.repo.db.commit()
                return True
        
        return False

    def close_return(self, return_id: int) -> bool:
        return_obj = self.repo.get_return_by_id(return_id)
        
        # Check return is OPEN
        if not return_obj or return_obj.status != "OPEN":
            return False
        
        self.repo.close_return(return_id)
        
        # Restore product quantities to inventory
        for returned_product in return_obj.returned_products:
            product = self.repo.db.query(ProductTypeDAO).filter(
                ProductTypeDAO.id == returned_product.product_type_id
            ).first()
            if product:
                product.quantity += returned_product.quantity
                self.repo.db.commit()
        
        return True

    def reimburse_return(self, return_id: int) -> Optional[dict]:
        return_obj = self.repo.get_return_by_id(return_id)
        
        # Check return is CLOSED
        if not return_obj or return_obj.status != "CLOSED":
            return None
        
        # Get the original sale to retrieve unit prices
        sale = self.repo.db.query(SaleTransactionDAO).filter(
            SaleTransactionDAO.id == return_obj.sale_transaction_id
        ).first()
        
        if not sale:
            return None
        
        # Calculate refund amount based on original sale prices
        refund_amount = 0.0
        for returned_product in return_obj.returned_products:
            # Find the product in the original sale to get the unit price paid
            for sale_line in sale.sale_lines:
                if sale_line.product_type_id == returned_product.product_type_id:
                    # Calculate refund: unit_price * returned_quantity * (1 - line_discount)
                    line_refund = returned_product.quantity * sale_line.unit_price * (1 - sale_line.discount_rate)
                    refund_amount += line_refund
                    break
        
        # Apply sale-level discount to refund amount
        refund_amount = refund_amount * (1 - sale.discount_rate)
        
        self.repo.mark_reimbursed(return_id)
        
        # Update shop balance (debit operation - refund decreases balance)
        system_info = self.repo.db.query(SystemInfoDAO).first()
        if system_info:
            system_info.balance -= refund_amount
            self.repo.db.commit()
        
        return {"refund_amount": round(refund_amount, 2)}
