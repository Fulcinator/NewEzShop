from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.DAO.returnTransaction_dao import ReturnTransactionDAO
from app.models.DAO.return_product_association import ReturnProductAssociation
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DAO.sale_product_association import SaleProductAssociation
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.DAO.debit_dao import DebitDAO

from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError


class ReturnRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------- helper ----------

    async def _get_sale_or_404(self, sale_id: int) -> SaleTransactionDAO:
        result = await self.db.execute(
            select(SaleTransactionDAO)
            .options(selectinload(SaleTransactionDAO.lines))
            .where(SaleTransactionDAO.id == sale_id)
        )
        sale = result.scalar_one_or_none()
        if not sale:
            raise NotFoundError("Sale not found")
        return sale

    async def _get_return_or_404(self, return_id: int) -> ReturnTransactionDAO:
        result = await self.db.execute(
            select(ReturnTransactionDAO)
            .options(selectinload(ReturnTransactionDAO.product_lines))
            .where(ReturnTransactionDAO.id == return_id)
        )
        ret = result.scalar_one_or_none()
        if not ret:
            raise NotFoundError("Return not found")
        return ret

    async def _get_system_info(self) -> SystemInfoDAO:
        result = await self.db.execute(select(SystemInfoDAO))
        sys = result.scalar_one_or_none()
        if not sys:
            sys = SystemInfoDAO(balance=0.0)
            self.db.add(sys)
            await self.db.commit()
            await self.db.refresh(sys)
        return sys

    # ---------- CRUD base ----------

    from sqlalchemy.orm import selectinload

    async def create_return(self, sale_id: int) -> ReturnTransactionDAO:
        sale = await self._get_sale_or_404(sale_id)

        # only paid sales can be returned
        if sale.status != "PAID":
            raise InvalidStateError("Return allowed only on closed and paid sales")

        ret = ReturnTransactionDAO(
            sale_transaction_id=sale.id,
            status="OPEN",
        )
        self.db.add(ret)
        await self.db.commit()
        await self.db.refresh(ret)

        # 🔴 IMPORTANT: reload with the relationships already loaded (even if empty)
        result = await self.db.execute(
            select(ReturnTransactionDAO)
            .options(selectinload(ReturnTransactionDAO.product_lines))
            .where(ReturnTransactionDAO.id == ret.id)
        )
        ret_loaded = result.scalar_one()

        return ret_loaded

    async def get_return_by_id(self, return_id: int) -> Optional[ReturnTransactionDAO]:
        return await self._get_return_or_404(return_id)

    async def get_all_returns(self) -> List[ReturnTransactionDAO]:
        result = await self.db.execute(
            select(ReturnTransactionDAO).options(
                selectinload(ReturnTransactionDAO.product_lines)
            )
        )
        return result.scalars().all()

    async def get_returns_by_sale_id(self, sale_id: int) -> List[ReturnTransactionDAO]:
        result = await self.db.execute(
            select(ReturnTransactionDAO)
            .options(selectinload(ReturnTransactionDAO.product_lines))
            .where(ReturnTransactionDAO.sale_transaction_id == sale_id)
        )
        return result.scalars().all()

    async def delete_return(self, return_id: int) -> bool:
        ret = await self._get_return_or_404(return_id)

        # do not allow deletion of reimbursed returns
        if ret.status == "REIMBURSED":
            raise InvalidStateError("Cannot delete a reimbursed return")

        await self.db.delete(ret)
        await self.db.commit()
        return True

    # ---------- handle return lines ----------

    async def add_product_to_return(self, return_id: int, barcode: str, amount: int):
        if amount <= 0:
            raise BadRequestError("Amount must be positive")

        ret = await self._get_return_or_404(return_id)

        if ret.status != "OPEN":
            raise InvalidStateError("Cannot modify a closed return")

        # sale associated
        sale = await self._get_sale_or_404(ret.sale_transaction_id)
        if sale.status != "PAID":
            raise InvalidStateError("Return allowed only on closed and paid sales")

        # product by barcode
        result = await self.db.execute(
            select(ProductTypeDAO).where(ProductTypeDAO.barcode == barcode)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")

        # lines of sale (one per barcode per how we structured the sales)
        result = await self.db.execute(
            select(SaleProductAssociation).where(
                SaleProductAssociation.sale_transaction_id == sale.id,
                SaleProductAssociation.product_barcode == barcode,
            )
        )
        sale_line = result.scalar_one_or_none()
        if not sale_line:
            raise BadRequestError("Product was not sold in this sale")

        # total quantity sold
        sold_qty = sale_line.quantity

        # quantity already returned (all returns of that sale for that product)
        result = await self.db.execute(
            select(func.coalesce(func.sum(ReturnProductAssociation.quantity), 0)).where(
                ReturnProductAssociation.product_type_id == product.id
            ).join(ReturnTransactionDAO, ReturnProductAssociation.return_transaction_id == ReturnTransactionDAO.id
            ).where(ReturnTransactionDAO.sale_transaction_id == sale.id)
        )
        already_returned = result.scalar() or 0

        if already_returned + amount > sold_qty:
            raise BadRequestError("Returned quantity exceeds sold quantity")

        # existing return line for this return+product?
        result = await self.db.execute(
            select(ReturnProductAssociation).where(
                ReturnProductAssociation.return_transaction_id == ret.id,
                ReturnProductAssociation.product_type_id == product.id,
            )
        )
        ret_line = result.scalar_one_or_none()

        if ret_line:
            ret_line.quantity += amount
        else:
            ret_line = ReturnProductAssociation(
                return_transaction_id=ret.id,
                product_type_id=product.id,
                quantity=amount,
                product_barcode=product.barcode,
                unit_price=sale_line.unit_price,
            )
            ret.product_lines.append(ret_line)
            self.db.add(ret_line)

        await self.db.commit()
        await self.db.refresh(ret_line)

    async def remove_product_from_return(self, return_id: int, barcode: str, amount: int):
        if amount <= 0:
            raise BadRequestError("Amount must be positive")

        ret = await self._get_return_or_404(return_id)

        if ret.status != "OPEN":
            raise InvalidStateError("Cannot remove items from a closed return")

        result = await self.db.execute(
            select(ProductTypeDAO).where(ProductTypeDAO.barcode == barcode)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")

        result = await self.db.execute(
            select(ReturnProductAssociation).where(
                ReturnProductAssociation.return_transaction_id == ret.id,
                ReturnProductAssociation.product_type_id == product.id,
            )
        )
        ret_line = result.scalar_one_or_none()
        if not ret_line:
            raise NotFoundError("Product not found in return")

        if amount >= ret_line.quantity:
            if ret_line in ret.product_lines:
                    ret.product_lines.remove(ret_line)
            await self.db.delete(ret_line)
        else:
            ret_line.quantity -= amount

        await self.db.commit()

    # ---------- closing and reimbursement ----------

    async def close_return(self, return_id: int):
        ret = await self._get_return_or_404(return_id)

        if ret.status != "OPEN":
            raise InvalidStateError("Invalid Return state to be closed")

        # restore quantity to warehouse
        for line in ret.product_lines:
            result = await self.db.execute(
                select(ProductTypeDAO).where(ProductTypeDAO.id == line.product_type_id)
            )
            product = result.scalar_one_or_none()
            if product:
                product.quantity += line.quantity

        ret.status = "CLOSED"
        ret.closed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(ret)

    async def reimburse_return(self, return_id: int) -> dict:
        ret = await self._get_return_or_404(return_id)

        if ret.status != "CLOSED":
            raise InvalidStateError("Return must be closed before reimbursement")

        sale = await self._get_sale_or_404(ret.sale_transaction_id)
        if sale.status != "PAID":
            raise InvalidStateError("Return allowed only on closed and paid sales")

        # calculate refund amount based on original prices and discounts
        refund_amount = 0.0

        for line in ret.product_lines:
            # find the corresponding sale line
            result = await self.db.execute(
                select(SaleProductAssociation).where(
                    SaleProductAssociation.sale_transaction_id == sale.id,
                    SaleProductAssociation.product_type_id == line.product_type_id,
                )
            )
            sale_line = result.scalar_one_or_none()
            if not sale_line:
                continue

            line_refund = (
                line.quantity
                * sale_line.unit_price
                * (1 - sale_line.discount_rate)
            )
            refund_amount += line_refund

        # global discount of the sale
        refund_amount *= (1 - sale.discountRate)

        # update return status
        ret.status = "REIMBURSED"

        # update system balance + register Debit
        sys = await self._get_system_info()
        sys.balance -= refund_amount

        debit = DebitDAO(
            amount=refund_amount,
            description=f"Refund for return #{ret.id}",
            date=datetime.utcnow(),
            account_book_id=1,
            return_transaction_id=ret.id,
        )
        self.db.add(debit)

        await self.db.commit()
        await self.db.refresh(ret)
        await self.db.refresh(sys)

        return {"refund_amount": round(refund_amount, 2)}