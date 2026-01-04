from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List, Optional

from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DAO.sale_product_association import SaleProductAssociation
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError

class SaleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_by_barcode(self, barcode: str) -> Optional[ProductTypeDAO]:
        result = await self.db.execute(
            select(ProductTypeDAO).where(ProductTypeDAO.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def create_sale(self, sale_data: dict) -> SaleTransactionDAO:
        sale = SaleTransactionDAO(**sale_data)
        self.db.add(sale)
        await self.db.commit()
        await self.db.refresh(sale)
        return sale

    async def get_all_sales(self) -> List[SaleTransactionDAO]:
        stmt = (
            select(SaleTransactionDAO)
            .options(selectinload(SaleTransactionDAO.lines))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_sale_by_id(self, sale_id: int) -> Optional[SaleTransactionDAO]:
        stmt = (
            select(SaleTransactionDAO)
            .where(SaleTransactionDAO.id == sale_id)
            .options(selectinload(SaleTransactionDAO.lines))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def delete_sale(self, sale_id: int) -> bool:
        result = await self.db.execute(
            delete(SaleTransactionDAO).where(SaleTransactionDAO.id == sale_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def add_product_to_sale(self, sale_id: int, barcode: str, amount: int):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be OPEN
        if sale.status != "OPEN":
            raise InvalidStateError("Cannot modify the sale")

        # 3. Quantity valid?
        if amount <= 0:
            raise BadRequestError("Amount must be positive")

        # 4. Product exists?
        product = await self.get_product_by_barcode(barcode)
        if not product:
            raise NotFoundError("Product not found")

        # 5. Stock sufficient?
        if product.quantity < amount:
            raise BadRequestError("Insufficient stock")

        # 6. Deduction of stock
        product.quantity -= amount

        # 7. create association line
        line = SaleProductAssociation(
            sale_transaction_id=sale_id,
            product_type_id=product.id,
            product_barcode=product.barcode,
            quantity=amount,
            unit_price=product.price_per_unit,
            discount_rate=0.0
        )

        self.db.add(line)
        await self.db.commit()
        await self.db.refresh(line)

        return line


    async def remove_product_from_sale(self, sale_id: int, barcode: str, amount: int):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be OPEN
        if sale.status != "OPEN":
            raise InvalidStateError("Cannot modify the sale")

        # 3. Quantity valid?
        if amount <= 0:
            raise BadRequestError("Amount must be positive")

        # 4. Product exists?
        product = await self.get_product_by_barcode(barcode)
        if not product:
            raise NotFoundError("Product not found")

        # 5. Line exists in sale?
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale_id,
                SaleProductAssociation.product_barcode == barcode
            )
        )
        line = result.scalar_one_or_none()
        if not line:
            raise NotFoundError("Product not found in sale")

        # 6. Removal or reduction of quantity
        if amount >= line.quantity:
            # reintegrate all
            product.quantity += line.quantity
            await self.db.delete(line)
        else:
            # reintegrate only the removed part
            product.quantity += amount
            line.quantity -= amount

        await self.db.commit()
        return True


    async def apply_discount_to_sale(self, sale_id: int, discount_rate: float):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be OPEN
        if sale.status != "OPEN":
            raise InvalidStateError("Cannot modify the sale")

        # 3. Discount valid?
        if discount_rate < 0.0 or discount_rate > 1.0:
            raise BadRequestError("Invalid discount rate")

        # 4. Apply discount
        sale.discountRate = discount_rate

        await self.db.commit()
        await self.db.refresh(sale)

        return sale


    async def apply_discount_to_product(self, sale_id: int, barcode: str, discount_rate: float):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be OPEN
        if sale.status != "OPEN":
            raise InvalidStateError("Cannot modify the sale")

        # 3. Discount valid?
        if discount_rate < 0.0 or discount_rate > 1.0:
            raise BadRequestError("Invalid discount rate")

        # 4. Product exists?
        product = await self.get_product_by_barcode(barcode)
        if not product:
            raise NotFoundError("Product not found")

        # 5. Line exists in sale?
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale_id,
                SaleProductAssociation.product_barcode == barcode
            )
        )
        line = result.scalar_one_or_none()
        if not line:
            raise NotFoundError("Product not found in sale")

        # 6. Apply discount
        line.discount_rate = discount_rate

        await self.db.commit()
        await self.db.refresh(line)

        return line


    async def close_sale(self, sale_id: int):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be OPEN
        if sale.status != "OPEN":
            raise InvalidStateError("Cannot modify the sale")

        # 3. Check if the sale is empty
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale_id
            )
        )
        lines = result.scalars().all()

        if len(lines) == 0:
            # 4. Sale empty → DELETE
            await self.db.delete(sale)
            await self.db.commit()
            return {"deleted": True}

        # 5. Sale not empty → close (PENDING)
        sale.status = "PENDING"
        await self.db.commit()
        await self.db.refresh(sale)

    async def pay_sale(self, sale_id: int, cash_amount: float):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale should be PENDING
        if sale.status != "PENDING":
            raise InvalidStateError("Cannot modify the sale")

        # 3. cash_amount valid?
        if cash_amount < 0:
            raise BadRequestError("Cash amount cannot be negative")

        # 4. Calculate total of the sale
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale_id
            )
        )
        lines = result.scalars().all()

        total = 0.0
        for line in lines:
            total += line.unit_price * line.quantity * (1 - line.discount_rate)

        # 5. Apply global discount of the sale (if present)
        total = total * (1 - sale.discountRate)

        # 6. Check if the customer has given enough money
        if cash_amount < total:
            raise BadRequestError("Insufficient cash amount")

        # 7. Calculate change
        change = round(cash_amount - total, 2)

        # 8. Update sale status
        sale.status = "PAID"

        # 9. Update system balance
        result = await self.db.execute(select(SystemInfoDAO))
        sys = result.scalar_one_or_none()

        if not sys:
            sys = SystemInfoDAO(balance=0.0)
            self.db.add(sys)
            await self.db.commit()
            await self.db.refresh(sys)
        sys.balance += total

        await self.db.commit()
        await self.db.refresh(sale)
        await self.db.refresh(sys)

        return {"change": change}


    async def compute_points(self, sale_id: int):
        # 1. Sale exists?
        sale = await self.get_sale_by_id(sale_id)
        if not sale:
            raise NotFoundError("Sale not found")

        # 2. Sale must be PAID
        if sale.status != "PAID":
            raise InvalidStateError("Sale must be paid to compute points")

        # 3. retrieve lines
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale_id
            )
        )
        lines = result.scalars().all()

        # 4. Calculate net total
        total = 0.0
        for line in lines:
            total += line.unit_price * line.quantity * (1 - line.discount_rate)

        total *= (1 - sale.discountRate)

        # 5. Calculate points (e.g., 1 point every euro)
        points = int(total)

        return {"points": points}
