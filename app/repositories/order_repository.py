from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.order_status import OrderStatus
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError

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

    async def issue_reorder_warning(
        self, product_type_id: int, supplier: str, quantity: int, price_per_unit: float
    ) -> OrderDAO:
        """
        Issue a reorder warning (create order in ISSUED state)
        """
        if quantity <= 0:
            raise BadRequestError("Quantity must be > 0")
        if price_per_unit <= 0:
            raise BadRequestError("Price per unit must be > 0")

        async with await self._get_session() as session:
            pt = await self._get_product_type_or_404(session, product_type_id)

            order = OrderDAO(
                supplier=supplier,
                status=OrderStatus.ISSUED,
                quantity=quantity,
                price_per_unit=price_per_unit,
            )
            order.product_types.append(pt)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def send_and_pay_order(
        self, product_type_id: int, supplier: str, quantity: int, price_per_unit: float
    ) -> OrderDAO:
        """
        Send and pay an order for a product type. Creates order directly in PAYED state
        """
        if quantity <= 0:
            raise BadRequestError("Quantity must be > 0")
        if price_per_unit <= 0:
            raise BadRequestError("Price per unit must be > 0")

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
            # TODO: handle balance / debit from accountant here later?
            await session.commit()
            await session.refresh(order)
            return order

    async def pay_issued_order(self, order_id: int) -> OrderDAO:
        """
        Pay an issued reorder warning (ISSUED -> PAYED)
        """
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            if not order:
                raise NotFoundError(f"Order with id '{order_id}' not found")

            if order.status != OrderStatus.ISSUED:
                raise BadRequestError("Only ISSUED orders can be payed")

            order.status = OrderStatus.PAYED
            # TODO: add accounting (debit) here later?
            await session.commit()
            await session.refresh(order)
            return order

    async def record_arrival(self, order_id: int) -> OrderDAO:
        """
        Record order arrival, and update product quantity (PAYED -> COMPLETED)
        """
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
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

    async def list_orders(self) -> List[OrderDAO]:
        """
        List all orders
        """
        async with await self._get_session() as session:
            stmt = select(OrderDAO)
            result = await session.execute(stmt)
            return result.scalars().unique().all()
