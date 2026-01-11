from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.user_dao import UserDAO
from app.models.DTO.order_dto import OrderProductTypeDTO, OrderResponseDTO
from app.models.DTO.sale_product_association_dto import SaleProductAssociationDTO
from app.models.DTO.user_dto import UserDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO
from app.models.DTO.product_type_dto import ProductTypeResponseDTO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DTO.saleTransaction_dto import SaleTransactionDTO
from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO
from app.models.DAO.returnTransaction_dao import ReturnTransactionDAO
from app.models.DTO.return_product_association_dto import ReturnProductAssociationDTO


def create_error_dto(code: int, message: str, name: str) -> ErrorDTO:
    """Create an ErrorDTO instance"""
    return ErrorDTO(code=code, message=message, name=name)

def create_token_dto(token: str) -> TokenDTO:
    return TokenDTO(token=token)

def userdao_to_dto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        password=user_dao.password,
        type=user_dao.type
    )

def userdao_to_responsedto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        type=user_dao.type
    )

def ProductTypeDao_toDto(product_type_dao: ProductTypeDAO, dto_class: ProductTypeResponseDTO) -> ProductTypeResponseDTO:
    pos = product_type_dao.position
    position_str = f"{pos.aisleID}-{pos.rackID}-{pos.levelID}" if pos else None
    return dto_class(
        id=product_type_dao.id,
        barcode=product_type_dao.barcode,
        description=product_type_dao.description,
        price_per_unit=product_type_dao.price_per_unit,
        quantity=product_type_dao.quantity,
        discountRate=product_type_dao.discountRate,
        note=product_type_dao.note,
        position=position_str
    )

def saleTransactionDao_toDto(
    sale_dao: SaleTransactionDAO,
    dto_class: SaleTransactionDTO,
    include_lines: bool = False
) -> SaleTransactionDTO:

    # exclude lines (es. POST /sales)
    if not include_lines:
        return dto_class(
            sale_transaction_id=sale_dao.id,
            status=sale_dao.status,
            cost=sale_dao.cost,
            payment_type=sale_dao.paymentType,
            discount_rate=sale_dao.discountRate,
            created_at=sale_dao.created_at,
            closed_at=sale_dao.closed_at,
            loyalty_card_id=sale_dao.loyalty_card_id,
            lines=[]
        )

    # include lines (GET)
    line_dtos = [
        SaleProductAssociationDTO(
            id=line.id,
            sale_transaction_id=line.sale_transaction_id,
            product_barcode=line.product_barcode,
            quantity=line.quantity,
            unit_price=line.unit_price,
            discount_rate=line.discount_rate
        )
        for line in sale_dao.lines
    ]

    return dto_class(
        sale_transaction_id=sale_dao.id,
        status=sale_dao.status,
        cost=sale_dao.cost,
        payment_type=sale_dao.paymentType,
        discount_rate=sale_dao.discountRate,
        created_at=sale_dao.created_at,
        closed_at=sale_dao.closed_at,
        loyalty_card_id=sale_dao.loyalty_card_id,
        lines=line_dtos
    )

def ReturnTransactionDao_toDto(return_dao: ReturnTransactionDAO, dto_class: ReturnTransactionDTO) -> ReturnTransactionDTO:
    line_dtos = [
        ReturnProductAssociationDTO(
            id=line.id,
            return_id=line.return_transaction_id,
            product_barcode=line.product_barcode,
            quantity=line.quantity,
            price_per_unit=line.unit_price,
        )
        for line in return_dao.product_lines
    ]

    return dto_class(
        id=return_dao.id,
        sale_id=return_dao.sale_transaction_id,
        status=return_dao.status,
        created_at=return_dao.created_at,
        closed_at=return_dao.closed_at,
        lines=line_dtos,
    )

def orderDao_toDto(order: OrderDAO) -> OrderResponseDTO:
    return OrderResponseDTO(
        order_id=order.id,
        supplier=order.supplier,
        status=order.status.value,
        quantity=order.quantity,
        price_per_unit=order.price_per_unit,
        issue_date=order.issue_date.isoformat(),
        product_types=[
            OrderProductTypeDTO(
                product_type_id=pt.id,
                barcode=pt.barcode,
                description=pt.description,
                quantity=pt.quantity
            )
            for pt in order.product_types
        ]
    )