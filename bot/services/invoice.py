from typing import Union, List
from schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from database.repositories.invoice_repo import InvoiceRepository
from database.models.invoice import Invoice

class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository):
        self.invoice_repo = invoice_repo

    async def create_invoice(self, invoice_data: InvoiceCreate) -> InvoiceResponse:
        invoice = Invoice(
            user_id=invoice_data.user_id,
            amount=invoice_data.amount,
            is_payed=False
        )
        created_invoice = await self.invoice_repo.add(invoice)
        return InvoiceResponse.model_validate(created_invoice)

    async def get_invoice(self, id: int) -> Union[InvoiceResponse, None]:
        invoice = await self.invoice_repo.get(id)
        if invoice:
            return InvoiceResponse.model_validate(invoice)
        return None

    async def get_invoices_by_user_id(self, user_id: int) -> List[InvoiceResponse]:
        invoices = await self.invoice_repo.get_by_user_id(user_id)
        return [InvoiceResponse.model_validate(inv) for inv in invoices]

    async def get_unpaid_invoices(self) -> List[InvoiceResponse]:
        invoices = await self.invoice_repo.get_unpaid_invoices()
        return [InvoiceResponse.model_validate(inv) for inv in invoices]

    async def mark_invoice_as_paid(self, invoice_id: int) -> bool:
        return await self.invoice_repo.mark_as_paid(invoice_id)

    async def delete_unpaid_invoice(self, invoice_id: int) -> bool:
        return await self.invoice_repo.delete_unpaid_invoice(invoice_id)

    async def update_invoice(self, id: int, invoice_data: InvoiceUpdate) -> Union[InvoiceResponse, None]:
        invoice = await self.invoice_repo.get(id)
        if invoice:
            for field, value in invoice_data.model_dump(exclude_unset=True).items():
                setattr(invoice, field, value)
            updated_invoice = await self.invoice_repo.update(invoice)
            return InvoiceResponse.model_validate(updated_invoice)
        return None

    async def delete_invoice(self, id: int) -> bool:
        return await self.invoice_repo.delete(id)
