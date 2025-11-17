from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from database.models.invoice import Invoice
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class InvoiceRepository(AsyncSQLAlchemyRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Invoice)

    async def get_by_user_id(self, user_id: int) -> List[Invoice]:
        """
        Получить все счета для конкретного пользователя (по telegram_id).
        """
        stmt = select(Invoice).where(Invoice.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_as_paid(self, invoice_id: int) -> bool:
        """
        Отметить счёт как оплаченный.
        Возвращает True, если счёт был найден и обновлён.
        """
        stmt = (
            update(Invoice)
            .where(Invoice.id == invoice_id, not Invoice.is_payed)
            .values(is_payed=True)
        )
        result = await self.session.execute(stmt)
        updated = result.rowcount > 0
        return updated

    async def get_unpaid_invoices(self) -> List[Invoice]:
        """
        Получить все неоплаченные счета.
        """
        stmt = select(Invoice).where(not Invoice.is_payed)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_unpaid_invoice(self, invoice_id: int) -> bool:
        """
        Удалить счёт, если он не оплачен.
        Возвращает True, если счёт был найден и удалён.
        """
        stmt = (
            delete(Invoice)
            .where(Invoice.id == invoice_id, not Invoice.is_payed)
        )
        result = await self.session.execute(stmt)
        deleted = result.rowcount > 0
        return deleted

    async def get_with_user(self, invoice_id: int) -> Union[Invoice, None]:
        """
        Получить счёт по ID, включая информацию о пользователе.
        """
        stmt = select(Invoice).options(selectinload(Invoice.user)).where(Invoice.id == invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()