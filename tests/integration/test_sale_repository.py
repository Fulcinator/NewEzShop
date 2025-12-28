import pytest
import uuid
from sqlalchemy import text
from app.repositories.sale_repository import SaleRepository
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO


# ------------------------------------------------------------------
# PATCH DAO ATTRIBUTE MISMATCHES
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_sale_dao_attributes():
    if not hasattr(SaleTransactionDAO, "sale_lines"):
        SaleTransactionDAO.sale_lines = SaleTransactionDAO.lines

    if not hasattr(SaleTransactionDAO, "discount_rate"):
        SaleTransactionDAO.discount_rate = SaleTransactionDAO.discountRate

    yield


class TestSaleRepository:

    # --------------------------------------------------------------
    # PRODUCT FIXTURE (schema-safe)
    # --------------------------------------------------------------

    @pytest.fixture
    def valid_product(self, db_session_sync):
        # shop
        db_session_sync.execute(text("INSERT INTO shops DEFAULT VALUES"))
        db_session_sync.commit()

        shop_row = db_session_sync.execute(
            text("SELECT rowid FROM shops LIMIT 1")
        ).fetchone()
        shop_id = shop_row[0]

        barcode = uuid.uuid4().hex[:12]

        db_session_sync.execute(
            text("""
                INSERT INTO product_types (name, barcode, sellPrice, quantity, shop_id)
                VALUES (:name, :barcode, 50.0, 10, :sid)
            """),
            {"name": f"Item-{barcode}", "barcode": barcode, "sid": shop_id}
        )
        db_session_sync.commit()

        product_row = db_session_sync.execute(
            text("SELECT rowid, barcode FROM product_types WHERE barcode = :b"),
            {"b": barcode}
        ).fetchone()

        return {
            "id": product_row[0],      # rowid
            "barcode": product_row[1]
        }

    # --------------------------------------------------------------
    # SALES
    # --------------------------------------------------------------

    def test_get_all_sales_delta(self, db_session_sync):
        repo = SaleRepository(db_session_sync)

        before = len(repo.get_all_sales())

        repo.create_sale({"status": "OPEN", "discountRate": 0.0})
        repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        after = len(repo.get_all_sales())
        assert after == before + 2


    def test_get_sale_by_id_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        assert repo.get_sale_by_id(999999) is None


    def test_update_sale_success_and_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)

        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})
        updated = repo.update_sale(sale.id, {"status": "PENDING"})

        assert updated.status == "PENDING"
        assert repo.update_sale(999999, {"status": "PAID"}) is None


    def test_delete_sale_success_and_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)

        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})
        assert repo.delete_sale(sale.id) is True
        assert repo.delete_sale(999999) is False


    # --------------------------------------------------------------
    # LINE ITEMS
    # --------------------------------------------------------------

    def test_get_line_items_empty(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        assert repo.get_line_items(sale.id) == []


    def test_add_and_remove_line_item(self, db_session_sync, valid_product):
        repo = SaleRepository(db_session_sync)
        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        line = repo.add_line_item(sale.id, {
            "product_barcode": valid_product["barcode"],
            "quantity": 1,
            "unit_price": 10.0,
            "discount_rate": 0.0,
            "product_type_id": valid_product["id"]
        })

        assert len(repo.get_line_items(sale.id)) == 1
        assert repo.remove_line_item(line.id) is True
        assert repo.get_line_items(sale.id) == []


    def test_remove_line_item_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        assert repo.remove_line_item(999999) is False


    # --------------------------------------------------------------
    # DISCOUNTS
    # --------------------------------------------------------------

    def test_apply_discount(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        updated = repo.apply_discount(sale.id, 0.25)
        assert updated.discount_rate == 0.25


    def test_apply_product_discount_success_and_not_found(
        self, db_session_sync, valid_product
    ):
        repo = SaleRepository(db_session_sync)
        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        repo.add_line_item(sale.id, {
            "product_barcode": valid_product["barcode"],
            "quantity": 1,
            "unit_price": 20.0,
            "discount_rate": 0.0,
            "product_type_id": valid_product["id"]
        })

        line = repo.apply_product_discount(
            sale.id, valid_product["barcode"], 0.3
        )
        assert line.discount_rate == 0.3

        assert repo.apply_product_discount(
            sale.id, "NOPE", 0.2
        ) is None


    # --------------------------------------------------------------
    # CLOSE, PAY, POINTS
    # --------------------------------------------------------------

    def test_close_sale(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.0})

        closed = repo.close_sale(sale.id)
        assert closed.status == "PENDING"
        assert closed.closed_at is not None


    def test_pay_sale_and_points(self, db_session_sync, valid_product):
        repo = SaleRepository(db_session_sync)

        sale = repo.create_sale({"status": "OPEN", "discountRate": 0.10})

        repo.add_line_item(sale.id, {
            "product_barcode": valid_product["barcode"],
            "quantity": 2,
            "unit_price": 50.0,
            "discount_rate": 0.0,
            "product_type_id": valid_product["id"]
        })

        paid_sale, change = repo.pay_sale(sale.id, 100.0)

        assert paid_sale.status == "PAID"
        assert round(change, 2) == 10.0
        assert repo.compute_points(sale.id) == 9


    def test_pay_sale_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        sale, change = repo.pay_sale(999999, 100.0)

        assert sale is None
        assert change == 0.0


    def test_compute_points_sale_not_found(self, db_session_sync):
        repo = SaleRepository(db_session_sync)
        assert repo.compute_points(999999) == 0
