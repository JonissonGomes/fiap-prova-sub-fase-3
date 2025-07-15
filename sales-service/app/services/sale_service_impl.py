from typing import List, Optional
from app.domain.sale import Sale, PaymentStatus
from app.schemas.sale_schema import SaleCreate, SaleUpdate
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from datetime import datetime


class SaleServiceImpl:
    def __init__(self, repository: MongoDBSaleRepository):
        self.repository = repository

    async def create_sale(self, sale_data: Sale) -> Sale:
        """Cria uma nova venda usando o objeto de domínio."""
        return await self.repository.save(sale_data)

    async def get_sale(self, sale_id: str) -> Optional[Sale]:
        """Obtém uma venda pelo ID."""
        return await self.repository.find_by_id(sale_id)

    async def get_sale_by_vehicle_id(self, vehicle_id: str) -> Optional[Sale]:
        """Obtém uma venda pelo ID do veículo."""
        return await self.repository.find_by_vehicle_id(vehicle_id)

    async def get_all_sales(self) -> List[Sale]:
        """Lista todas as vendas."""
        return await self.repository.find_all()

    async def get_sales_by_status(self, status: str) -> List[Sale]:
        """Lista vendas por status."""
        return await self.repository.find_by_status(status)

    async def update_sale(self, sale_id: str, sale_data: SaleUpdate) -> Optional[Sale]:
        """Atualiza uma venda existente."""
        existing = await self.repository.find_by_id(sale_id)
        if not existing:
            return None

        # Atualiza apenas os campos fornecidos
        update_fields = sale_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        return await self.repository.update(existing)

    async def delete_sale(self, sale_id: str) -> bool:
        """Remove uma venda."""
        return await self.repository.delete(sale_id)

    async def update_payment_status(self, sale_id: str, status: PaymentStatus) -> Optional[Sale]:
        """Atualiza o status de pagamento de uma venda."""
        sale = await self.repository.find_by_id(sale_id)
        if not sale:
            return None
        
        sale.payment_status = status
        sale.updated_at = datetime.utcnow()
        return await self.repository.update(sale)

    async def get_sale_by_payment_code(self, payment_code: str) -> Optional[Sale]:
        """Busca uma venda pelo código de pagamento."""
        return await self.repository.find_by_payment_code(payment_code)

        sale = await self.repository.find_by_payment_code(payment_code)
        if not sale:
            raise Exception("Venda não encontrada")
        return sale
