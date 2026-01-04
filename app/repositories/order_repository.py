from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.database.database import AsyncSessionLocal
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO
from app.models.DAO.credit_dao import CreditDAO
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.errors.balance_error import BalanceError
from app.models.order_status import OrderStatus
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.ordes_errors import GeneralError, InvalidStateError

class OrderRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def _get_product_type_or_404(self, session: AsyncSession, product_type_id: int) -> ProductTypeDAO:
        pt = await session.get(ProductTypeDAO, product_type_id)
        if not pt:
            raise NotFoundError(f"Product type with id '{product_type_id}' not found")
        return pt

    async def _get_balance(self, session):
        result = await session.execute(
            select(func.sum(BalanceOperationDAO.amount))
        )
        return result.scalar() or 0
    
    async def issue_reorder_warning(
        self, product_barcode: str, quantity: int, price_per_unit: float
    ) -> OrderDAO:
        if quantity <= 0:
            raise BadRequestError("Quantity must be > 0")
        if price_per_unit <= 0:
            raise BadRequestError("Price per unit must be > 0")

        async with await self._get_session() as session:
            # Find product type by barcode
            result = await session.execute(
                select(ProductTypeDAO).where(ProductTypeDAO.barcode == product_barcode)
            )
            pt = result.scalars().first()
            if not pt:
                raise NotFoundError(f"Product type with barcode '{product_barcode}' not found")

            order = OrderDAO(
                supplier=None,  # Supplier is unknown for reorder warnings
                status=OrderStatus.ISSUED,
                quantity=quantity,
                price_per_unit=price_per_unit,
            )
            order.product_types.append(pt)
            session.add(order)
            await session.commit()

            stmt = (
                select(OrderDAO)
                .where(OrderDAO.id == order.id)
                .options(selectinload(OrderDAO.product_types))
            )
            result = await session.execute(stmt)
            return result.scalar_one()

    async def create_and_pay_order(
        self, product_barcode: str, quantity: int, price_per_unit: float
    ) -> OrderDAO:

        if quantity <= 0:
            raise BadRequestError("Quantity must be > 0")
        if price_per_unit <= 0:
            raise BadRequestError("Price per unit must be > 0")

        async with await self._get_session() as session:

            # 1. find product type by barcode
            result = await session.execute(
                select(ProductTypeDAO).where(ProductTypeDAO.barcode == product_barcode)
            )
            pt = result.scalars().first()
            if not pt:
                raise NotFoundError(f"Product type with barcode '{product_barcode}' not found")

            # 2. Calculate total cost
            total_cost = quantity * price_per_unit

            # 3. Verify balance
            current_balance = await self._get_balance(session)
            if current_balance - total_cost < 0:
                raise BalanceError("Insufficient balance for the operation")

            # 4. Create order in PAYED state
            order = OrderDAO(
                supplier=None,
                status=OrderStatus.PAYED,
                quantity=quantity,
                price_per_unit=price_per_unit
            )
            order.product_types.append(pt)
            session.add(order)
            await session.flush()

            # 5. Register the negative credit
            credit = CreditDAO(
                amount=-total_cost,
                sale_transaction_id=None
            )
            session.add(credit)

            # 6. Commit
            await session.commit()

            # 7. Reload order with relationship
            stmt = (
                select(OrderDAO)
                .where(OrderDAO.id == order.id)
                .options(selectinload(OrderDAO.product_types))
            )
            result = await session.execute(stmt)
            return result.scalar_one()
        
    async def pay_issued_and_update_balance(self, order_id: int):
        async with await self._get_session() as session:

            # 1. Retrieve order
            stmt = (
                select(OrderDAO)
                .where(OrderDAO.id == order_id)
                .options(selectinload(OrderDAO.product_types))
            )
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise NotFoundError(f"Order with id '{order_id}' not found")

            if order.status != OrderStatus.ISSUED:
                raise InvalidStateError("order is not paid")

            if not order.product_types:
                raise GeneralError("Position must be set for an order before its arrival")

            # 2. Calculate total cost
            total_cost = order.quantity * order.price_per_unit

            # 3. Verify balance
            current_balance = await self._get_balance(session)
            if current_balance - total_cost < 0:
                raise BalanceError("Insufficient balance for the operation")

            # 4. Update order status
            order.status = OrderStatus.PAYED

            # 5. Register negative credit
            credit = CreditDAO(amount=-total_cost)
            session.add(credit)

            # 6. Commit
            await session.commit()

    async def record_arrival_and_update_quantity(self, order_id: int):
        async with await self._get_session() as session:

            # 1. Retrieve order with product types
            stmt = (
                select(OrderDAO)
                .where(OrderDAO.id == order_id)
                .options(selectinload(OrderDAO.product_types))
            )
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise NotFoundError(f"Order with id '{order_id}' not found")

            # 2. Must be PAYED
            if order.status != OrderStatus.PAYED:
                raise InvalidStateError("order is not paid")

            # 3. Must have a product type associated
            if not order.product_types:
                raise GeneralError("Position must be set for an order before its arrival")
            product_type = order.product_types[0]

            # 4. Update product quantity
            product_type.quantity += order.quantity

            # 5. Update order status
            order.status = OrderStatus.COMPLETED

            # 6. Commit final
            await session.commit()
            
    async def list_orders(self,status=None) -> List[OrderDAO]:
        async with await self._get_session() as session:
            stmt = select(OrderDAO).options(selectinload(OrderDAO.product_types))
            if status is not None:
                stmt = stmt.where(OrderDAO.status == status)
            result = await session.execute(stmt)
            return result.scalars().unique().all()
""" not used anymore
    async def send_and_pay_order(
        self, product_type_id: int, supplier: str, quantity: int, price_per_unit: float
    ) -> OrderDAO:
        if quantity <= 0: raise BadRequestError("Quantity must be > 0")
        if price_per_unit <= 0: raise BadRequestError("Price per unit must be > 0")

        async with await self._get_session() as session:
            pt = await self._get_product_type_or_404(session, product_type_id)

            order = OrderDAO(
                supplier=supplier,
                status=OrderStatus.PAYED,
                quantity=quantity,
                price_per_unit=price_per_unit,
            )
            order.product_types.append(pt)
            session.add(order)
            await session.commit()
            
            stmt = select(OrderDAO).where(OrderDAO.id == order.id).options(selectinload(OrderDAO.product_types))
            result = await session.execute(stmt)
            return result.scalar_one()

    async def pay_issued_order(self, order_id: int) -> OrderDAO:
        async with await self._get_session() as session:
            stmt = select(OrderDAO).where(OrderDAO.id == order_id).options(selectinload(OrderDAO.product_types))
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                raise NotFoundError(f"Order with id '{order_id}' not found")
            if order.status != OrderStatus.ISSUED:
                raise BadRequestError("Only ISSUED orders can be payed")

            order.status = OrderStatus.PAYED
            await session.commit()
            await session.refresh(order)
            return order

    async def record_arrival(self, order_id: int) -> OrderDAO:
        async with await self._get_session() as session:
            stmt = select(OrderDAO).where(OrderDAO.id == order_id).options(selectinload(OrderDAO.product_types))
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                raise NotFoundError(f"Order with id '{order_id}' not found")
            if order.status != OrderStatus.PAYED:
                raise BadRequestError("Only PAYED orders can be completed")
            if not order.product_types:
                raise BadRequestError("Order has no associated product type")

            product_type = order.product_types[0]
            product_type.quantity += order.quantity
            order.status = OrderStatus.COMPLETED

            await session.commit()
            await session.refresh(order)
            return order
"""
