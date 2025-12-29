import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user_type import UserType
from app.models.DAO.user_dao import UserDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError


@pytest.mark.asyncio
class TestUserRepository:

    async def test_create_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        user = await repo.create_user(
            username=f"user_{uuid.uuid4().hex[:6]}",
            password="secret",
            user_type=UserType.Administrator
        )

        assert user.id is not None
        assert user.username.startswith("user_")
        assert user.type == UserType.Administrator

    async def test_create_user_conflict(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        username = f"user_{uuid.uuid4().hex[:6]}"

        await repo.create_user(username, "pw", UserType.Cashier)

        with pytest.raises(ConflictError):
            await repo.create_user(username, "pw2", UserType.ShopManager)

    async def test_get_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        user = await repo.create_user(
            username=f"user_{uuid.uuid4().hex[:6]}",
            password="pw",
            user_type=UserType.Cashier
        )

        fetched = await repo.get_user(user.id)

        assert fetched.id == user.id
        assert fetched.username == user.username

    async def test_get_user_not_found(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.get_user(99999)

    async def test_get_user_by_username_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        username = f"user_{uuid.uuid4().hex[:6]}"

        await repo.create_user(username, "pw", UserType.ShopManager)

        user = await repo.get_user_by_username(username)

        assert user.username == username

    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.get_user_by_username("does_not_exist")

    async def test_list_users(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        await repo.create_user(f"user1_{uuid.uuid4().hex[:4]}", "pw", UserType.Cashier)
        await repo.create_user(f"user2_{uuid.uuid4().hex[:4]}", "pw", UserType.Administrator)

        users = await repo.list_users()

        assert len(users) >= 2
        assert all(isinstance(u, UserDAO) for u in users)

    async def test_update_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        user = await repo.create_user(
            username=f"user_{uuid.uuid4().hex[:6]}",
            password="old",
            user_type=UserType.Cashier
        )

        updated = await repo.update_user(
            user_id=user.id,
            updated_username=f"updated_{uuid.uuid4().hex[:6]}",
            password="new",
            type=UserType.ShopManager
        )

        assert updated.username.startswith("updated_")
        assert updated.password == "new"
        assert updated.type == UserType.ShopManager

    async def test_update_user_not_found(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        result = await repo.update_user(
            user_id=9999,
            updated_username="x",
            password="y",
            type=UserType.Administrator
        )

        assert result is None

    async def test_update_user_conflict(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        user1 = await repo.create_user(
            username="userA",
            password="pw",
            user_type=UserType.Cashier
        )
        user2 = await repo.create_user(
            username="userB",
            password="pw",
            user_type=UserType.ShopManager
        )

        with pytest.raises(ConflictError):
            await repo.update_user(
                user_id=user2.id,
                updated_username=user1.username,
                password="pw",
                type=UserType.ShopManager
            )

    async def test_delete_user_success(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        user = await repo.create_user(
            username=f"user_{uuid.uuid4().hex[:6]}",
            password="pw",
            user_type=UserType.Cashier
        )

        result = await repo.delete_user(user.id)

        assert result is True

        with pytest.raises(NotFoundError):
            await repo.get_user(user.id)

    async def test_delete_user_not_found(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.delete_user(9999)

    async def test_search_users_no_filters_returns_all(self, db_session: AsyncSession):
        repo = UserRepository(db_session)

        await repo.create_user(f"user_{uuid.uuid4().hex[:4]}", "pw", UserType.Cashier)
        await repo.create_user(f"user_{uuid.uuid4().hex[:4]}", "pw", UserType.Administrator)

        users = await repo.search_users()

        assert len(users) >= 2

    async def test_search_users_by_username(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        username = f"user_{uuid.uuid4().hex[:6]}"

        await repo.create_user(username, "pw", UserType.Cashier)
        await repo.create_user("other", "pw", UserType.Cashier)

        users = await repo.search_users(username=username)

        assert len(users) == 1
        assert users[0].username == username

    async def test_search_users_by_type(self, db_session):
        repo = UserRepository(db_session)

        await repo.create_user(
            f"user_{uuid.uuid4().hex[:6]}",
            "pw",
            UserType.Cashier
        )
        await repo.create_user(
            f"admin_{uuid.uuid4().hex[:6]}",
            "pw",
            UserType.Administrator
        )

        users = await repo.search_users(user_type=UserType.Administrator)

        assert len(users) >= 1
        assert all(u.type == UserType.Administrator for u in users)

