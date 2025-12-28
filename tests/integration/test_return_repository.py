import pytest
import uuid
from sqlalchemy import text
from app.repositories.return_repository import ReturnRepository

class TestReturnRepository:

    @pytest.fixture
    def base_data(self, db_session_sync):
        """Creates parent records with all discovered required fields."""
        db_session_sync.execute(text("INSERT INTO shops DEFAULT VALUES"))
        db_session_sync.commit()
        shop_row = db_session_sync.execute(text("SELECT * FROM shops LIMIT 1")).fetchone()
        shop_id = shop_row[0]

        unique_barcode = uuid.uuid4().hex[:12]
        db_session_sync.execute(text("""
            INSERT INTO product_types (name, barcode, sellPrice, quantity, shop_id) 
            VALUES (:name, :barcode, 50.0, 10, :sid)
        """), {"name": f"Item-{unique_barcode[:4]}", "barcode": unique_barcode, "sid": shop_id})
        db_session_sync.commit()
        product_row = db_session_sync.execute(text("SELECT * FROM product_types LIMIT 1")).fetchone()
        product_id = product_row[0]

        db_session_sync.execute(text("""
            INSERT INTO sale_transactions (status, discountRate, cost, created_at) 
            VALUES ('PAID', 0.0, 50.0, CURRENT_TIMESTAMP)
        """))
        db_session_sync.commit()
        sale_row = db_session_sync.execute(text("SELECT * FROM sale_transactions LIMIT 1")).fetchone()
        sale_id = sale_row[0]

        return {"sale_id": sale_id, "product_id": product_id}

    def test_return_lifecycle_full(self, db_session_sync, base_data):
        repo = ReturnRepository(db_session_sync)
        sale_id = base_data["sale_id"]
        product_id = base_data["product_id"]

        return_txn = repo.create_return({
            "sale_transaction_id": sale_id,
            "status": "OPEN"
        })
        
        return_id = getattr(return_txn, 'id', None) or \
                    getattr(return_txn, 'return_transaction_id', None)
        
        assert return_id is not None

        assoc = repo.add_returned_product(return_id, {
            "product_type_id": product_id,
            "quantity": 1
        })
        assert assoc is not None
        
        products = repo.get_returned_products(return_id)
        assert len(products) == 1

        updated = repo.mark_reimbursed(return_id)
        assert updated.status == "REIMBURSED"

    def test_get_returns_by_sale_id(self, db_session_sync, base_data):
        repo = ReturnRepository(db_session_sync)
        sale_id = base_data["sale_id"]
        
        repo.create_return({"sale_transaction_id": sale_id, "status": "OPEN"})
        
        returns = repo.get_returns_by_sale_id(sale_id)
        assert len(returns) >= 1

    def test_close_return(self, db_session_sync, base_data):
        repo = ReturnRepository(db_session_sync)
        ret = repo.create_return({"sale_transaction_id": base_data["sale_id"], "status": "OPEN"})
        ret_id = getattr(ret, 'id', None) or getattr(ret, 'return_transaction_id', None)

        closed = repo.close_return(ret_id)
        assert closed.status == "CLOSED"
        assert closed.closed_at is not None

    def test_remove_returned_product(self, db_session_sync, base_data):
        repo = ReturnRepository(db_session_sync)
        ret = repo.create_return({"sale_transaction_id": base_data["sale_id"]})
        ret_id = getattr(ret, 'id', None) or getattr(ret, 'return_transaction_id', None)

        assoc = repo.add_returned_product(ret_id, {
            "product_type_id": base_data["product_id"],
            "quantity": 1
        })
        
        assoc_id = getattr(assoc, 'id', None) or getattr(assoc, 'return_product_id', None)
        
        result = repo.remove_returned_product(assoc_id)
        assert result is True
        assert len(repo.get_returned_products(ret_id)) == 0

    def test_delete_return(self, db_session_sync, base_data):
        repo = ReturnRepository(db_session_sync)
        ret = repo.create_return({"sale_transaction_id": base_data["sale_id"]})
        ret_id = getattr(ret, 'id', None) or getattr(ret, 'return_transaction_id', None)
        
        success = repo.delete_return(ret_id)
        assert success is True
        assert repo.get_return_by_id(ret_id) is None