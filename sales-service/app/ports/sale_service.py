from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.sale import Sale
from ..schemas.sale_schema import SaleCreate, SaleUpdate, SaleResponse

class SaleService(ABC):
    """Interface para o serviço de vendas."""
    
    @abstractmethod
    async def create_sale(self, sale: SaleCreate) -> SaleResponse:
        """Cria uma nova venda."""
        pass

    @abstractmethod
    async def get_sale(self, sale_id: str) -> SaleResponse:
        """Obtém uma venda pelo ID."""
        pass

    @abstractmethod
    async def get_sale_by_vehicle_id(self, vehicle_id: str) -> Optional[Sale]:
        """Obtém uma venda pelo ID do veículo."""
        pass

    @abstractmethod
    async def get_all_sales(self) -> List[Sale]:
        """Lista todas as vendas."""
        pass

    @abstractmethod
    async def get_sales_by_status(self, status: str) -> List[Sale]:
        """Lista vendas por status."""
        pass

    @abstractmethod
    async def update_sale(self, sale_id: str, sale_update: SaleUpdate) -> SaleResponse:
        """Atualiza uma venda existente."""
        pass

    @abstractmethod
    async def delete_sale(self, sale_id: str) -> None:
        """Remove uma venda."""
        pass

    @abstractmethod
    async def update_payment_status(self, payment_code: str, status: str) -> Optional[Sale]:
        """Atualiza o status de pagamento de uma venda."""
        pass 